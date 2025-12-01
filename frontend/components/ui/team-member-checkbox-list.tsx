"use client"

import { TEAM_MEMBERS } from "@/lib/team-members"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface TeamMemberCheckboxListProps {
  selected: string[];
  onChange: (selected: string[]) => void;
  label?: string;
  className?: string;
}

export function TeamMemberCheckboxList({
  selected,
  onChange,
  label,
  className,
}: TeamMemberCheckboxListProps) {
  const handleToggle = (member: string) => {
    if (selected.includes(member)) {
      onChange(selected.filter((m) => m !== member));
    } else {
      onChange([...selected, member]);
    }
  };

  const handleSelectAll = () => {
    onChange([...TEAM_MEMBERS]);
  };

  const handleClear = () => {
    onChange([]);
  };

  return (
    <div className={cn("space-y-3", className)}>
      {label && (
        <label className="text-sm font-medium">{label}</label>
      )}
      <div className="flex gap-2 mb-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleSelectAll}
        >
          Select All
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleClear}
        >
          Clear
        </Button>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {TEAM_MEMBERS.map((member) => (
          <label
            key={member}
            className="flex items-center gap-2 cursor-pointer text-sm p-2 rounded hover:bg-gray-50"
          >
            <Checkbox
              checked={selected.includes(member)}
              onCheckedChange={() => handleToggle(member)}
            />
            <span>{member}</span>
          </label>
        ))}
      </div>
      {selected.length > 0 && (
        <p className="text-xs text-gray-500">
          {selected.length} selected
        </p>
      )}
    </div>
  )
}
