/*
 * Read-only, local export helper for Blackboard Ultra.
 *
 * After signing into https://tcd.blackboard.com, open the Blackboard page you
 * want to inspect, paste this into the browser DevTools console, and save the
 * downloaded JSON outside this repository. It never sends data anywhere.
 *
 * This is intentionally conservative. Blackboard's DOM changes by course and
 * release, so selectors are broad and should be refined against Carlos's
 * authenticated pages before relying on it for reminders.
 */
(() => {
  const text = (node) => (node?.innerText || "").replace(/\s+/g, " ").trim();
  const dedupe = (rows, key) => [...new Map(rows.filter(Boolean).map((row) => [key(row), row])).values()];
  const links = [...document.querySelectorAll('a[href]')];
  const courses = dedupe(
    links
      .filter((a) => /\/ultra\/courses\//.test(a.href))
      .map((a) => ({ id: a.href, title: text(a), url: a.href }))
      .filter((course) => course.title),
    (course) => course.id,
  );
  const announcementNodes = [
    ...document.querySelectorAll('[data-testid*="announcement" i], [class*="announcement" i]'),
  ];
  const announcements = dedupe(
    announcementNodes.map((node) => ({
      title: text(node.querySelector('h1,h2,h3,h4,strong')) || text(node).slice(0, 120),
      course: document.title,
      posted_at: "",
      body: text(node),
      url: location.href,
    })),
    (announcement) => `${announcement.title}|${announcement.body}`,
  );
  const dueNodes = [...document.querySelectorAll('[data-testid*="due" i], [class*="due" i]')];
  const work_items = dedupe(
    dueNodes.map((node) => ({
      title: text(node.querySelector('a,h1,h2,h3,h4,strong')) || text(node).slice(0, 120),
      course: document.title,
      due_at: text(node),
      details: text(node),
      url: location.href,
    })),
    (item) => `${item.title}|${item.due_at}`,
  );
  const exportData = {
    schema_version: 1,
    exported_at: new Date().toISOString(),
    source: "Trinity College Dublin Blackboard Ultra",
    courses,
    work_items,
    announcements,
  };
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
  const a = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(blob),
    download: 'blackboard-export.json',
  });
  a.click();
  URL.revokeObjectURL(a.href);
  console.log(`Exported ${courses.length} courses, ${work_items.length} work items, and ${announcements.length} announcements.`);
})();
