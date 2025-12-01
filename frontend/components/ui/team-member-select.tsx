"use client"

import { TEAM_MEMBERS } from "@/lib/team-members"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

const UNASSIGNED_VALUE = "__unassigned__";

interface TeamMemberSelectProps {
  value: string | undefined;
  onValueChange: (value: string) => void;
  placeholder?: string;
  allowEmpty?: boolean;
  className?: string;
}

export function TeamMemberSelect({
  value,
  onValueChange,
  placeholder = "Select team member",
  allowEmpty = false,
  className,
}: TeamMemberSelectProps) {
  const handleValueChange = (newValue: string) => {
    onValueChange(newValue === UNASSIGNED_VALUE ? "" : newValue);
  };

  // Normalize value: treat undefined and empty string the same way
  const normalizedValue = value ?? "";

  // Convert empty/undefined to special value for allowEmpty, or undefined to show placeholder
  const displayValue = normalizedValue === ""
    ? (allowEmpty ? UNASSIGNED_VALUE : undefined)
    : normalizedValue;

  return (
    <Select value={displayValue} onValueChange={handleValueChange}>
      <SelectTrigger className={cn("w-full", className)}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {allowEmpty && (
          <SelectItem value={UNASSIGNED_VALUE}>Unassigned</SelectItem>
        )}
        {TEAM_MEMBERS.map((member) => (
          <SelectItem key={member} value={member}>
            {member}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
