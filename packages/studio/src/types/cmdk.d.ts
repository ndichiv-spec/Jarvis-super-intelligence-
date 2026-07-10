declare module "cmdk" {
  import * as React from "react";

  interface CommandProps {
    children?: React.ReactNode;
    className?: string;
    [key: string]: unknown;
  }

  interface CommandItemProps {
    children?: React.ReactNode;
    value?: string;
    onSelect?: (value: string) => void;
    className?: string;
    disabled?: boolean;
    [key: string]: unknown;
  }

  interface CommandGroupProps {
    children?: React.ReactNode;
    heading?: string;
    className?: string;
    [key: string]: unknown;
  }

  interface CommandListProps {
    children?: React.ReactNode;
    className?: string;
    [key: string]: unknown;
  }

  interface CommandInputProps {
    value?: string;
    onValueChange?: (value: string) => void;
    placeholder?: string;
    className?: string;
    ref?: React.Ref<HTMLInputElement>;
    [key: string]: unknown;
  }

  export const Command: React.FC<CommandProps> & {
    Item: React.FC<CommandItemProps>;
    Group: React.FC<CommandGroupProps>;
    List: React.FC<CommandListProps>;
    Input: React.FC<CommandInputProps>;
    Empty: React.FC<{ children?: React.ReactNode }>;
  };
}
