import pandas as pd
from typing import List, Dict
from backend.models.dataset import CandidateRelationship

class RelationshipDetector:
    """Detects primary key / foreign key candidate relationships across multiple datasets."""

    @classmethod
    def detect_relationships(cls, datasets: Dict[str, pd.DataFrame]) -> List[CandidateRelationship]:
        candidates: List[CandidateRelationship] = []
        dataset_names = list(datasets.keys())

        for i in range(len(dataset_names)):
            for j in range(i + 1, len(dataset_names)):
                name1 = dataset_names[i]
                name2 = dataset_names[j]
                df1 = datasets[name1]
                df2 = datasets[name2]

                for col1 in df1.columns:
                    for col2 in df2.columns:
                        c1_str, c2_str = str(col1), str(col2)
                        
                        # Match on exact column name or ID suffix match
                        names_match = (c1_str.lower() == c2_str.lower())
                        id_suffix_match = ("id" in c1_str.lower() and "id" in c2_str.lower() and 
                                           (c1_str.lower().replace("_id", "") in c2_str.lower() or 
                                            c2_str.lower().replace("_id", "") in c1_str.lower()))

                        if names_match or id_suffix_match:
                            s1 = df1[col1].dropna()
                            s2 = df2[col2].dropna()

                            if len(s1) == 0 or len(s2) == 0:
                                continue

                            set1 = set(s1.unique())
                            set2 = set(s2.unique())
                            intersection = set1.intersection(set2)

                            if len(intersection) > 0:
                                overlap_ratio = len(intersection) / max(len(set1), len(set2))
                                is1_unique = len(s1) == len(set1)
                                is2_unique = len(s2) == len(set2)

                                confidence = round(0.5 * (1.0 if names_match else 0.8) + 0.5 * overlap_ratio, 2)

                                candidates.append(CandidateRelationship(
                                    left_dataset=name1,
                                    left_column=c1_str,
                                    right_dataset=name2,
                                    right_column=c2_str,
                                    confidence=confidence,
                                    reason=f"Column name match ('{c1_str}' ↔ '{c2_str}') with {len(intersection)} overlapping values.",
                                    is_left_unique=is1_unique,
                                    is_right_unique=is2_unique
                                ))

        candidates.sort(key=lambda r: r.confidence, reverse=True)
        return candidates
