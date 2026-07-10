import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricChart } from "@/components/shared/metric-chart";

describe("MetricChart", () => {
  const data = [
    { label: "Mon", value: 10 },
    { label: "Tue", value: 20 },
    { label: "Wed", value: 15 },
  ];

  it("renders title", () => {
    render(<MetricChart title="Weekly Activity" data={data} />);
    expect(screen.getByText("Weekly Activity")).toBeInTheDocument();
  });

  it("renders data labels", () => {
    render(<MetricChart title="Test" data={data} />);
    expect(screen.getByText("Mon")).toBeInTheDocument();
    expect(screen.getByText("Wed")).toBeInTheDocument();
  });

  it("renders with empty data", () => {
    const { container } = render(<MetricChart title="Empty" data={[]} />);
    expect(container.querySelector("div")).toBeInTheDocument();
  });
});
