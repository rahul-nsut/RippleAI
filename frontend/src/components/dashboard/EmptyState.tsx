import PageCard from "../../components/dashboard/PageCard";

export default function EmptyState() {
  return (
    <>
      <h2 className="mb-4 text-lg font-semibold">
        List of Pages in your Confluence Space
      </h2>

      <div className="flex gap-4 overflow-x-auto pb-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <PageCard key={i} title="Consumer GraphQL API" summary="This page explains the consumer-facing GraphQL APIs used to fetch match statistics and player performance data." url="https://example.com" />
        ))}
      </div>
    </>
  );
}
