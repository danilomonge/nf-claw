// One page-scroll lock shared by every overlay (command palette, mobile menu). Each holder takes
// the lock and releases it; the page scrolls again only when the last holder lets go, whatever
// order they close in.

let holders = 0;

export function lockScroll(): () => void {
  holders += 1;
  document.documentElement.style.overflow = "hidden";
  let released = false;
  return () => {
    if (released) return;
    released = true;
    holders = Math.max(0, holders - 1);
    if (holders === 0) document.documentElement.style.overflow = "";
  };
}
