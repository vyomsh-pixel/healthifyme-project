export default function ComingSoon({ title }) {
  return (
    <div className="max-w-3xl mx-auto px-10 py-12">
      <h1 className="font-display text-4xl font-semibold tracking-tight text-[var(--text-primary)] mb-3">
        {title}
      </h1>
      <p className="text-[var(--text-secondary)] text-sm">
        This page is next up for the React rewrite — Dashboard is the first
        slice, ported end-to-end so we can validate the approach before doing
        the rest.
      </p>
    </div>
  );
}