export default function DataQualityBadge({ dataQuality }) {
  if (!dataQuality) return null;
  const { completeness, flags } = dataQuality;
  const hasFlags = flags && flags.length > 0;

  return (
    <span
      title={hasFlags ? flags.join('; ') : `${completeness}% of expected fields present`}
      className={`inline-flex items-center gap-1 rounded-sm px-1.5 py-0.5 text-[11px] font-medium ${
        hasFlags ? 'bg-risk-medium-bg text-risk-medium' : 'bg-navy-50 text-navy-600'
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${hasFlags ? 'bg-risk-medium' : 'bg-navy-600'}`} />
      {completeness}% complete
    </span>
  );
}
