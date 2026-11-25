export const U = 11; // metres per map unit
export const DEPOT = { x: 60, y: 360 };

// Street list used for the register form and as the map's first frame. The live copy comes from the API.
export const STOPS = [
  [140, 300, 'Temple Rd'], [230, 345, 'Market Jn'], [330, 300, 'School Ln'],
  [430, 345, 'Bus Stand'], [520, 300, 'Lake Rd'], [520, 215, 'Hospital Rd'],
  [410, 215, 'Park Ave'], [300, 215, 'Clock Tower'], [140, 215, 'Station Rd'],
  [140, 105, 'Canal St'], [300, 105, 'Library Rd'], [410, 105, 'Beach Rd'],
].map(([x, y, n], i) => ({ id: i + 1, x, y, n }));

export const MATERIALS = ['Plastics', 'Glass', 'Paper', 'E-waste'];
export const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
export const FUEL_WEEK = [182, 176, 171, 163, 158, 149, 141]; // sample data
