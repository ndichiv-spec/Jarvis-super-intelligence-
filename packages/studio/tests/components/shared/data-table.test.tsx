import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DataTable } from "@/components/shared/data-table";
import type { Column } from "@/components/shared/data-table";

interface TestItem {
  id: string;
  name: string;
  role: string;
}

const columns: Column<TestItem>[] = [
  { key: "name", header: "Name", cell: (item) => item.name },
  { key: "role", header: "Role", cell: (item) => item.role },
];

const data: TestItem[] = [
  { id: "1", name: "Alice", role: "Engineer" },
  { id: "2", name: "Bob", role: "Designer" },
  { id: "3", name: "Charlie", role: "Manager" },
];

describe("DataTable", () => {
  it("renders column headers", () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Role")).toBeInTheDocument();
  });

  it("renders all data rows", () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Charlie")).toBeInTheDocument();
  });

  it("shows empty message when no data", () => {
    render(<DataTable columns={columns} data={[]} />);
    expect(screen.getByText("No data available")).toBeInTheDocument();
  });

  it("shows custom empty message", () => {
    render(<DataTable columns={columns} data={[]} emptyMessage="Nothing here" />);
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  it("applies cursor-pointer when onRowClick provided", () => {
    const { container } = render(<DataTable columns={columns} data={data} onRowClick={() => {}} />);
    const rows = container.querySelectorAll("tbody tr");
    expect(rows[0]).toHaveClass("cursor-pointer");
  });

  it("does not apply cursor-pointer when no onRowClick", () => {
    const { container } = render(<DataTable columns={columns} data={data} />);
    const rows = container.querySelectorAll("tbody tr");
    expect(rows[0]).not.toHaveClass("cursor-pointer");
  });

  it("renders correct number of rows", () => {
    const { container } = render(<DataTable columns={columns} data={data} />);
    const rows = container.querySelectorAll("tbody tr");
    expect(rows).toHaveLength(3);
  });

  it("applies custom className", () => {
    const { container } = render(<DataTable columns={columns} data={data} className="custom-table" />);
    expect(container.firstChild).toHaveClass("custom-table");
  });
});
