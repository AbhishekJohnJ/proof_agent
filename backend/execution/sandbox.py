import sys
import json
import shutil
import tempfile
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.execution.limits import ExecutionLimits
from backend.models.dataset import DatasetArtifact

class SandboxExecutionEnvironment(ABC):
    """Abstract sandbox environment interface."""

    @abstractmethod
    def execute(self, code: str, datasets: Optional[List[DatasetArtifact]] = None) -> Dict[str, Any]:
        raise NotImplementedError

class LocalIsolatedSandbox(SandboxExecutionEnvironment):
    """Development process sandbox using isolated workspace directory and process boundaries."""

    def __init__(self, limits: ExecutionLimits | None = None):
        self.limits = limits or ExecutionLimits()

    def execute(self, code: str, datasets: Optional[List[DatasetArtifact]] = None) -> Dict[str, Any]:
        datasets = datasets or []
        with tempfile.TemporaryDirectory(prefix="proofai_sandbox_") as tmpdir:
            tmp_path = Path(tmpdir)
            data_dir = tmp_path / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            # Copy selected datasets into sandbox
            selected_ids = set()
            for artifact in datasets:
                ds_dir = data_dir / artifact.dataset_id
                ds_dir.mkdir(parents=True, exist_ok=True)
                src_file = Path(artifact.workspace_path)
                if src_file.exists():
                    shutil.copy2(src_file, ds_dir / f"data{src_file.suffix.lower()}")
                    # Copy to filename.csv as well for compatibility
                    shutil.copy2(src_file, ds_dir / src_file.name)
                    selected_ids.add(artifact.dataset_id)

            # Enforce Least Privilege: ONLY mount contract authorized datasets!

            # Inject comprehensive runtime column access and operation tracking audit header
            audit_header = """import builtins, json, os, atexit
_proofai_accessed = set()
_proofai_cols = []
_proofai_ops = []

_orig_open = builtins.open
def _audit_open(file, *args, **kwargs):
    fstr = str(file)
    if "data/" in fstr or os.path.exists(fstr):
        _proofai_accessed.add(fstr)
    return _orig_open(file, *args, **kwargs)
builtins.open = _audit_open

try:
    import pandas as pd

    # Series comparison operator instrumentation for filter detection
    for op_name, op_symbol in [("__eq__", "=="), ("__ne__", "!="), ("__gt__", ">"), ("__lt__", "<"), ("__ge__", ">="), ("__le__", "<=")]:
        if hasattr(pd.Series, op_name):
            orig_comp = getattr(pd.Series, op_name)
            def _make_comp_wrapper(symbol, orig_c):
                def _comp_wrapper(self_series, other):
                    res = orig_c(self_series, other)
                    try:
                        res._proofai_op = symbol
                        res._proofai_val = other
                        res._proofai_col = getattr(self_series, "name", None)
                    except Exception:
                        pass
                    return res
                return _comp_wrapper
            setattr(pd.Series, op_name, _make_comp_wrapper(op_symbol, orig_comp))

    # GroupBy aggregations instrumentation
    try:
        from pandas.core.groupby.generic import SeriesGroupBy, DataFrameGroupBy
        for groupby_cls in [SeriesGroupBy, DataFrameGroupBy]:
            for agg_func in ["sum", "mean", "count", "nunique", "min", "max"]:
                if hasattr(groupby_cls, agg_func):
                    orig_gb_fn = getattr(groupby_cls, agg_func)
                    def _make_gb_agg_wrapper(fname, orig_fn):
                        def _gb_agg_wrapper(self_gb, *args, **kwargs):
                            sel = getattr(self_gb, "_selection", None) or getattr(self_gb, "name", None)
                            _proofai_ops.append({
                                "operation": "aggregate",
                                "column": str(sel) if sel is not None else None,
                                "function": fname
                            })
                            return orig_fn(self_gb, *args, **kwargs)
                        return _gb_agg_wrapper
                    setattr(groupby_cls, agg_func, _make_gb_agg_wrapper(agg_func, orig_gb_fn))
    except Exception:
        pass

    # Series aggregations instrumentation
    try:
        for agg_func in ["sum", "mean", "count", "nunique", "min", "max", "std", "var"]:
            if hasattr(pd.Series, agg_func):
                orig_s_fn = getattr(pd.Series, agg_func)
                def _make_s_agg_wrapper(fname, orig_fn):
                    def _s_agg_wrapper(self_s, *args, **kwargs):
                        ds_name = getattr(self_s, "_proofai_ds", None)
                        col_name = getattr(self_s, "_proofai_col", getattr(self_s, "name", None))
                        _proofai_ops.append({
                            "operation": "aggregate",
                            "dataset": ds_name,
                            "column": str(col_name) if col_name is not None else None,
                            "function": fname
                        })
                        return orig_fn(self_s, *args, **kwargs)
                    return _s_agg_wrapper
                setattr(pd.Series, agg_func, _make_s_agg_wrapper(agg_func, orig_s_fn))
    except Exception:
        pass

    _orig_read_csv = pd.read_csv
    def _audit_read_csv(filepath_or_buffer, *args, **kwargs):
        df = _orig_read_csv(filepath_or_buffer, *args, **kwargs)
        ds_name = str(filepath_or_buffer)
        df._proofai_ds = ds_name

    # DataFrame class methods instrumentation
    orig_df_getitem = pd.DataFrame.__getitem__
    def _audit_df_getitem(self, item):
        ds_name = getattr(self, "_proofai_ds", None)
        if isinstance(item, str):
            _proofai_cols.append({"dataset": ds_name, "column": item, "operation": "read"})
            res = orig_df_getitem(self, item)
            try:
                res._proofai_ds = ds_name
                res._proofai_col = item
            except Exception:
                pass
            return res
        elif isinstance(item, list):
            for col in item:
                if isinstance(col, str):
                    _proofai_cols.append({"dataset": ds_name, "column": col, "operation": "read"})
            _proofai_ops.append({"operation": "select", "columns": [str(c) for c in item]})
            return orig_df_getitem(self, item)
        elif hasattr(item, "dtype") and str(item.dtype).startswith("bool"):
            col_name = getattr(item, "_proofai_col", None) or getattr(item, "name", None)
            _proofai_ops.append({
                "operation": "filter",
                "dataset": ds_name,
                "column": str(col_name) if col_name is not None else None,
                "operator": getattr(item, "_proofai_op", "=="),
                "value": getattr(item, "_proofai_val", None)
            })
        return orig_df_getitem(self, item)
    pd.DataFrame.__getitem__ = _audit_df_getitem

    orig_df_merge = pd.DataFrame.merge
    def _audit_df_merge(self, right, *m_args, **m_kwargs):
        ds_name = getattr(self, "_proofai_ds", None)
        on = m_kwargs.get("on") or (m_args[0] if m_args else None)
        left_on = m_kwargs.get("left_on")
        right_on = m_kwargs.get("right_on")
        how = m_kwargs.get("how", "inner")
        r_ds = getattr(right, "_proofai_ds", None)
        _proofai_ops.append({
            "operation": "join",
            "left_dataset": ds_name,
            "right_dataset": r_ds,
            "left_column": str(left_on or on) if (left_on or on) else None,
            "right_column": str(right_on or on) if (right_on or on) else None,
            "on": str(on) if on else None,
            "how": how
        })
        res_df = orig_df_merge(self, right, *m_args, **m_kwargs)
        try:
            res_df._proofai_ds = ds_name
        except Exception:
            pass
        return res_df
    pd.DataFrame.merge = _audit_df_merge

    orig_df_groupby = pd.DataFrame.groupby
    def _audit_df_groupby(self, by, *g_args, **g_kwargs):
        ds_name = getattr(self, "_proofai_ds", None)
        by_cols = [str(by)] if isinstance(by, str) else [str(c) for c in by]
        _proofai_ops.append({
            "operation": "group_by",
            "dataset": ds_name,
            "column": by_cols[0] if len(by_cols) == 1 else None,
            "columns": by_cols
        })
        return orig_df_groupby(self, by, *g_args, **g_kwargs)
    pd.DataFrame.groupby = _audit_df_groupby

    orig_df_sort = pd.DataFrame.sort_values
    def _audit_df_sort(self, by, *s_args, **s_kwargs):
        by_cols = [str(by)] if isinstance(by, str) else [str(c) for c in by]
        ascending = s_kwargs.get("ascending", True)
        order = "asc" if ascending else "desc"
        _proofai_ops.append({
            "operation": "sort",
            "column": by_cols[0] if by_cols else None,
            "order": order
        })
        return orig_df_sort(self, by, *s_args, **s_kwargs)
    pd.DataFrame.sort_values = _audit_df_sort

    orig_df_head = pd.DataFrame.head
    def _audit_df_head(self, n=5):
        _proofai_ops.append({"operation": "limit", "value": n})
        return orig_df_head(self, n)
    pd.DataFrame.head = _audit_df_head

    _orig_pd_merge = pd.merge
    def _audit_pd_merge(left, right, *m_args, **m_kwargs):
        on = m_kwargs.get("on") or (m_args[0] if m_args else None)
        left_on = m_kwargs.get("left_on")
        right_on = m_kwargs.get("right_on")
        how = m_kwargs.get("how", "inner")
        left_ds = getattr(left, "_proofai_ds", None)
        right_ds = getattr(right, "_proofai_ds", None)
        _proofai_ops.append({
            "operation": "join",
            "left_dataset": left_ds,
            "right_dataset": right_ds,
            "left_column": str(left_on or on) if (left_on or on) else None,
            "right_column": str(right_on or on) if (right_on or on) else None,
            "on": str(on) if on else None,
            "how": how
        })
        res_df = _orig_pd_merge(left, right, *m_args, **m_kwargs)
        try:
            res_df._proofai_ds = left_ds
        except Exception:
            pass
        return res_df
    pd.merge = _audit_pd_merge

    _orig_read_csv = pd.read_csv
    def _audit_read_csv(filepath_or_buffer, *args, **kwargs):
        df = _orig_read_csv(filepath_or_buffer, *args, **kwargs)
        ds_name = str(filepath_or_buffer)
        try:
            df._proofai_ds = ds_name
        except Exception:
            pass
        return df
    pd.read_csv = _audit_read_csv
except Exception:
    pass

def _report_access():
    print("__PROOFAI_ACCESSED__:" + json.dumps(list(_proofai_accessed)))
    print("__PROOFAI_COLS__:" + json.dumps(_proofai_cols))
    print("__PROOFAI_OPS__:" + json.dumps(_proofai_ops))
atexit.register(_report_access)
"""
            full_script_code = audit_header + "\n" + code

            script_path = tmp_path / "script.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_script_code)

            try:
                res = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.limits.timeout_seconds
                )

                raw_stdout = res.stdout[:self.limits.max_output_bytes].strip()
                stderr = res.stderr[:self.limits.max_output_bytes].strip()

                # Extract accessed files, cols, ops from stdout
                accessed_files = []
                accessed_cols = []
                runtime_ops = []
                accessed_dataset_ids = []
                clean_stdout_lines = []

                for line in raw_stdout.splitlines():
                    if line.startswith("__PROOFAI_ACCESSED__:"):
                        try:
                            accessed_files = json.loads(line.replace("__PROOFAI_ACCESSED__:", ""))
                        except Exception:
                            pass
                    elif line.startswith("__PROOFAI_COLS__:"):
                        try:
                            accessed_cols = json.loads(line.replace("__PROOFAI_COLS__:", ""))
                        except Exception:
                            pass
                    elif line.startswith("__PROOFAI_OPS__:"):
                        try:
                            runtime_ops = json.loads(line.replace("__PROOFAI_OPS__:", ""))
                        except Exception:
                            pass
                    else:
                        clean_stdout_lines.append(line)

                stdout = "\n".join(clean_stdout_lines).strip()

                # Extract dataset IDs from accessed file paths
                for fpath in accessed_files:
                    parts = Path(fpath).parts
                    if "data" in parts:
                        idx = parts.index("data")
                        if idx + 1 < len(parts):
                            ds_id = parts[idx + 1]
                            if ds_id and ds_id not in accessed_dataset_ids and ds_id != "script.py":
                                accessed_dataset_ids.append(ds_id)

                parsed_output = None
                if stdout:
                    try:
                        for line in reversed(stdout.splitlines()):
                            line_str = line.strip()
                            if line_str.startswith("{") and line_str.endswith("}"):
                                parsed_output = json.loads(line_str)
                                break
                    except Exception:
                        parsed_output = None

                return {
                    "success": res.returncode == 0,
                    "returncode": res.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "parsed_output": parsed_output,
                    "accessed_files": accessed_files,
                    "accessed_dataset_ids": accessed_dataset_ids,
                    "accessed_columns": accessed_cols,
                    "runtime_operations": runtime_ops,
                    "execution_mode": "local_isolated",
                    "error": None if res.returncode == 0 else f"Process exited with code {res.returncode}: {stderr}"
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.limits.timeout_seconds} seconds.",
                    "parsed_output": None,
                    "accessed_files": [],
                    "accessed_dataset_ids": [],
                    "accessed_columns": [],
                    "runtime_operations": [],
                    "execution_mode": "local_isolated",
                    "error": f"Execution timed out after {self.limits.timeout_seconds} seconds."
                }
            except Exception as e:
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "parsed_output": None,
                    "accessed_files": [],
                    "accessed_dataset_ids": [],
                    "accessed_columns": [],
                    "runtime_operations": [],
                    "execution_mode": "local_isolated",
                    "error": f"Execution failed: {str(e)}"
                }

class DockerSandbox(SandboxExecutionEnvironment):
    """Production hardened Docker sandbox environment. NO SILENT FALLBACK to host execution when unavailable."""

    def __init__(self, limits: ExecutionLimits | None = None, docker_image: str = "proofai-sandbox:latest"):
        self.limits = limits or ExecutionLimits()
        self.docker_image = docker_image

    def execute(self, code: str, datasets: Optional[List[DatasetArtifact]] = None) -> Dict[str, Any]:
        datasets = datasets or []
        with tempfile.TemporaryDirectory(prefix="proofai_docker_ws_") as tmpdir:
            tmp_path = Path(tmpdir)
            data_dir = tmp_path / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            for artifact in datasets:
                ds_dir = data_dir / artifact.dataset_id
                ds_dir.mkdir(parents=True, exist_ok=True)
                src_file = Path(artifact.workspace_path)
                if src_file.exists():
                    shutil.copy2(src_file, ds_dir / f"data{src_file.suffix.lower()}")

            script_path = tmp_path / "script.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", f"{self.limits.max_memory_mb}m",
                "--cpus", "1.0",
                "-v", f"{tmp_path.resolve()}:/workspace:ro",
                "-w", "/workspace",
                self.docker_image,
                "python3", "/workspace/script.py"
            ]

            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.limits.timeout_seconds
                )
                stdout = res.stdout[:self.limits.max_output_bytes].strip()
                stderr = res.stderr[:self.limits.max_output_bytes].strip()

                parsed_output = None
                if stdout:
                    for line in reversed(stdout.splitlines()):
                        line_str = line.strip()
                        if line_str.startswith("{") and line_str.endswith("}"):
                            try:
                                parsed_output = json.loads(line_str)
                                break
                            except Exception:
                                pass

                return {
                    "success": res.returncode == 0,
                    "returncode": res.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "parsed_output": parsed_output,
                    "execution_mode": "docker_sandbox",
                    "error": None if res.returncode == 0 else stderr
                }
            except Exception as e:
                # Docker is unavailable - NO SILENT FALLBACK to host!
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Docker sandbox unavailable: {str(e)}",
                    "parsed_output": None,
                    "execution_mode": "docker_unavailable",
                    "error": "sandbox_unavailable"
                }
