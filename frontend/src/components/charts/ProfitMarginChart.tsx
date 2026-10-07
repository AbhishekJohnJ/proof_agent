import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

const data = [
  { product: 'Enterprise Suite', margin: 68.4 },
  { product: 'Analytics Addon', margin: 54.2 },
  { product: 'Cloud Storage', margin: 42.1 },
  { product: 'Professional Services', margin: 31.8 },
  { product: 'Hardware Gateway', margin: 18.5 },
];

export const ProfitMarginChart: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <div>
        <h4 className="text-sm font-semibold text-slate-100">Product Line Profit Margins (%)</h4>
        <p className="text-xs text-slate-400">Enterprise Suite leads margin profitability</p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={(v) => `${v}%`} />
            <YAxis type="category" dataKey="product" stroke="#64748b" fontSize={11} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#f8fafc',
              }}
              formatter={(val: any) => [`${val}%`, 'Gross Profit Margin']}
            />
            <Bar dataKey="margin" fill="#38bdf8" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
