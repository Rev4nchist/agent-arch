import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const responsiveDialogContent = (maxWidth: string = 'lg:max-w-[500px]') =>
  cn(
    'w-full h-full max-h-[100vh] fixed inset-0 rounded-none',
    'lg:w-auto lg:h-auto lg:max-h-[90vh] lg:inset-auto',
    'lg:top-[50%] lg:left-[50%] lg:translate-x-[-50%] lg:translate-y-[-50%]',
    'lg:rounded-lg overflow-y-auto',
    maxWidth
  )
