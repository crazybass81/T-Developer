'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement<LucideIcon>;
  trend?: string;
  target?: string;
  status?: 'healthy' | 'warning' | 'error' | 'neutral';
  constraint?: string;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  trend,
  target,
  status = 'neutral',
  constraint,
  className,
}) => {
  const statusColors = {
    healthy: 'text-green-600 bg-green-50 border-green-200',
    warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    error: 'text-red-600 bg-red-50 border-red-200',
    neutral: 'text-gray-600 bg-gray-50 border-gray-200',
  };

  const trendColor = trend?.startsWith('+') ? 'text-green-600' : trend?.startsWith('-') ? 'text-red-600' : 'text-gray-600';

  return (
    <div className={clsx(
      'p-6 rounded-lg border-2 transition-all hover:shadow-lg',
      statusColors[status],
      className
    )}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={clsx('p-2 rounded-lg', statusColors[status].split(' ')[1])}>
            {React.cloneElement(icon, { className: 'w-5 h-5' })}
          </div>
          <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        </div>
        {trend && (
          <span className={clsx('text-sm font-semibold', trendColor)}>
            {trend}
          </span>
        )}
      </div>

      <div className="space-y-2">
        <div className="text-2xl font-bold text-gray-900">{value}</div>

        {target && (
          <div className="text-xs text-gray-500">
            Target: <span className="font-medium">{target}</span>
          </div>
        )}

        {constraint && (
          <div className="text-xs text-gray-500">
            Constraint: <span className="font-medium">{constraint}</span>
          </div>
        )}
      </div>
    </div>
  );
};
