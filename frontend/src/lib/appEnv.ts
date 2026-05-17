export function showInternalUi(): boolean {
  if (process.env.NEXT_PUBLIC_SHOW_INTERNAL_UI === "true") {
    return true;
  }
  if (process.env.NEXT_PUBLIC_SHOW_INTERNAL_UI === "false") {
    return false;
  }
  return process.env.NODE_ENV !== "production";
}
