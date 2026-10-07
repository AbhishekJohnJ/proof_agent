import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

const data = [
  { month: 'Jul (Q3)', revenue: 3.9, formatted: '₹3.9L' },
  { month: 'Aug (Q3)', revenue: 4.1, formatted: '₹4.1L' },
  { month: 'Sep (Q3)', revenue: 4.4, formatted: '₹4.4L' },
  { month: 'Oct (Q4)', revenue: 4.6, formatted: '₹4.6L' },
  { month: 'Nov (Q4)', revenue: 4.9, formatted: '₹4.9L' },
  { month: 'Dec (Q4)', revenue: 5.2, formatted: '₹5.2L' },
];

export const RevenueGrowthChart: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <div>
        <h4 className="text-sm font-semibold text-slate-100">Monthly Revenue Trend (Q3 vs Q4)</h4>
        <p className="text-xs text-slate-400">Sequential growth culminating in ₹14.7L Q4 total</p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${v}L`} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#f8fafc',
              }}
              formatter={(value: any) => [`₹${value} Lakhs`, 'Revenue']}
            />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#6366f1"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorRev)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
