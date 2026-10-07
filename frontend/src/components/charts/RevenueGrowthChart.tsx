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
    <div className="bg-[#242726] border border-[#3C3B39] rounded-xl p-5 space-y-4">
      <div>
        <h4 className="text-sm font-bold text-[#F4F5EC]">Monthly Revenue Trend (Q3 vs Q4)</h4>
        <p className="text-xs text-[#F4F5EC]/60">Sequential growth culminating in ₹14.7L Q4 total</p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#E64A32" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#E64A32" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#3C3B39" vertical={false} />
            <XAxis dataKey="month" stroke="#F4F5EC" fontSize={11} tickLine={false} />
            <YAxis stroke="#F4F5EC" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${v}L`} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#151918',
                borderColor: '#3C3B39',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#F4F5EC',
              }}
              formatter={(value: any) => [`₹${value} Lakhs`, 'Revenue']}
            />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#E64A32"
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
