import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

const data = [
  { region: 'North', revenue: 5.8, share: '39.5%' },
  { region: 'West', revenue: 4.2, share: '28.6%' },
  { region: 'South', revenue: 2.9, share: '19.7%' },
  { region: 'East', revenue: 1.8, share: '12.2%' },
];

const colors = ['#E64A32', '#E18230', '#3C3B39', '#4D4B48'];

export const RegionRevenueChart: React.FC = () => {
  return (
    <div className="bg-[#242726] border border-[#3C3B39] rounded-xl p-5 space-y-4">
      <div>
        <h4 className="text-sm font-bold text-[#F4F5EC]">Q4 Regional Revenue Distribution</h4>
        <p className="text-xs text-[#F4F5EC]/60">North region generates highest revenue share</p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3C3B39" vertical={false} />
            <XAxis dataKey="region" stroke="#F4F5EC" fontSize={11} tickLine={false} />
            <YAxis stroke="#F4F5EC" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${v}L`} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#151918',
                borderColor: '#3C3B39',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#F4F5EC',
              }}
              formatter={(value: any, name: any, props: any) => [
                `₹${value} Lakhs (${props.payload.share})`,
                'Revenue',
              ]}
            />
            <Bar dataKey="revenue" radius={[6, 6, 0, 0]}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
