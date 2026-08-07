import React from 'react';
import { cn } from './Spinner';

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn("animate-pulse rounded-md bg-muted", className)} />
  );
};
