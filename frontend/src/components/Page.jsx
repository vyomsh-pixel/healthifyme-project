export default function Page({ children, className = "" }) {
  return <div className={`page-wrap ${className}`}>{children}</div>;
}

export { Page };
