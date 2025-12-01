export const TEAM_MEMBERS = [
  'Mark Beynon',
  'Dimitar Stoynev',
  'Boyan Asenov',
  'Borja Soler',
  'Alaster Sagar',
  'Lukasz Pelcner',
  'Danny Shine',
  'David Hayes',
] as const;

export type TeamMember = typeof TEAM_MEMBERS[number];
