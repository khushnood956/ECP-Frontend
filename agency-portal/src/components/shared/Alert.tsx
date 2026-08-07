import React from 'react';
import { cn } from './Spinner';

interface AlertProps {
  variant?: 'default' | 'destructive' | 'success';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({ variant = 'default', title, children, className }) => {
  const variants = {
    default: "bg-accent text-accent-foreground border-accent",
    destructive: "bg-destructive/15 text-destructive border-destructive/20",
    success: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50"
  };

  return (
    <div className={cn("p-4 rounded-md border", variants[variant], className)} role="alert">
      {title && <h5 className="mb-1 font-medium leading-none tracking-tight">{title}</h5>}
      <div className="text-sm [&_p]:leading-relaxed">
        {children}
      </div>
    </div>
  );
};
