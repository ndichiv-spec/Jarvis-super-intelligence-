import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { DataTable } from "@/components/shared/data-table";
import { StatusDot } from "@/components/shared/status-dot";
import { SectionHeader } from "@/components/shared/section-header";
import type { Column } from "@/components/shared/data-table";

describe("Accessibility", () => {
  it("Button has correct ARIA attributes", () => {
    render(<Button>Click me</Button>);
    const btn = screen.getByRole("button", { name: "Click me" });
    expect(btn).toBeInTheDocument();
  });

  it("Card is accessible", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
        </CardHeader>
        <CardContent>Content</CardContent>
      </Card>,
    );
    expect(screen.getByText("Card Title")).toBeInTheDocument();
    expect(screen.getByText("Content")).toBeInTheDocument();
  });

  it("Switch has correct role", () => {
    render(<Switch />);
    expect(screen.getByRole("switch")).toBeInTheDocument();
  });

  it("DataTable has proper table semantics", () => {
    const columns: Column<Record<string, unknown>>[] = [
      { key: "name", header: "Name", render: (item) => item.name as string },
    ];
    const data = [{ id: "1", name: "Test" }];
    const { container } = render(<DataTable columns={columns} data={data} keyField="id" />);
    expect(container.querySelector("table")).toBeInTheDocument();
    expect(container.querySelector("thead")).toBeInTheDocument();
    expect(container.querySelector("tbody")).toBeInTheDocument();
  });

  it("StatusDot has aria-label", () => {
    render(<StatusDot status="healthy" />);
    expect(screen.getByLabelText("Status: healthy")).toBeInTheDocument();
  });

  it("SectionHeader uses proper heading hierarchy", () => {
    render(<SectionHeader title="Section Title" />);
    expect(screen.getByRole("heading", { level: 3 })).toHaveTextContent("Section Title");
  });
});
