'use client';

import { useState, ReactNode } from 'react';
import { Filter, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from '@/components/ui/sheet';

interface MobileFilterBarProps {
  children: ReactNode;
  activeCount?: number;
  title?: string;
  className?: string;
}

export function MobileFilterBar({
  children,
  activeCount = 0,
  title = 'Filters',
  className = '',
}: MobileFilterBarProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Mobile: Filter button */}
      <div className={`block lg:hidden ${className}`}>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setOpen(true)}
          className="gap-2"
        >
          <Filter className="h-4 w-4" />
          {title}
          {activeCount > 0 && (
            <span className="rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
              {activeCount}
            </span>
          )}
        </Button>

        <Sheet open={open} onOpenChange={setOpen}>
          <SheetContent side="bottom" onCloseClick={() => setOpen(false)}>
            <SheetHeader>
              <SheetTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                {title}
              </SheetTitle>
            </SheetHeader>
            <div className="flex flex-col gap-4 p-4">
              {children}
            </div>
            <SheetFooter>
              <Button
                variant="outline"
                onClick={() => setOpen(false)}
                className="w-full"
              >
                Apply Filters
              </Button>
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop: Inline filters */}
      <div className={`hidden lg:flex lg:items-center lg:gap-4 ${className}`}>
        {children}
      </div>
    </>
  );
}
