import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DataTable } from "@/components/shared/data-table";
import type { Column } from "@/components/shared/data-table";

interface TestItem {
  id: string;
  name: string;
  role: string;
}

const columns: Column<TestItem>[] = [
  { key: "name", header: "Name", render: (item) => item.name, sortable: true },
  { key: "role", header: "Role", render: (item) => item.role },
];

const data: TestItem[] = [
  { id: "1", name: "Charlie", role: "Manager" },
  { id: "2", name: "Alice", role: "Engineer" },
  { id: "3", name: "Bob", role: "Designer" },
];

describe("DataTable", () => {
  it("renders all rows from data", () => {
    render(<DataTable columns={columns} data={data} keyField="id" />);
    expect(screen.getByText("Charlie")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
  });

  it("renders empty message when data is empty", () => {
    render(<DataTable columns={columns} data={[]} keyField="id" />);
    expect(screen.getByText("No data")).toBeInTheDocument();
  });

  it("renders custom empty message", () => {
    render(<DataTable columns={columns} data={[]} keyField="id" emptyMessage="Nothing here" />);
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  it("sorts by column when sortable header clicked", () => {
    render(<DataTable columns={columns} data={data} keyField="id" />);
    fireEvent.click(screen.getByText("Name"));
    const rows = screen.getAllByRole("row");
    expect(rows[1]).toHaveTextContent("Alice");
    expect(rows[2]).toHaveTextContent("Bob");
    expect(rows[3]).toHaveTextContent("Charlie");
  });

  it("toggles sort direction on click", () => {
    render(<DataTable columns={columns} data={data} keyField="id" />);
    const header = screen.getByText("Name");
    fireEvent.click(header);
    fireEvent.click(header);
    const rows = screen.getAllByRole("row");
    expect(rows[1]).toHaveTextContent("Charlie");
    expect(rows[2]).toHaveTextContent("Bob");
    expect(rows[3]).toHaveTextContent("Alice");
  });
});
