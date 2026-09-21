export let temporaryReferenceFile: File | null = null;

export const setTemporaryReferenceFile = (file: File | null) => {
  temporaryReferenceFile = file;
};

export const getTemporaryReferenceFile = () => {
  const file = temporaryReferenceFile;
  temporaryReferenceFile = null; // Clear immediately on read
  return file;
};
