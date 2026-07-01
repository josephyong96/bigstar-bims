# BIMS Frontend

Bigstar Inventory Management System - Frontend Application

## Tech Stack

- React 18 with TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- shadcn/ui (UI components)
- Zustand (state management)
- React Router (routing)

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
src/
  components/     # Reusable UI components
    layout/       # App layout, sidebar
    ui/           # shadcn/ui components
    shared/       # Shared components
  pages/          # Page components
  services/       # API services
  stores/         # State management
  types/          # TypeScript types
  lib/            # Utility functions
```

## Features

- Inventory management with barcode/serial/batch tracking
- Purchase order and delivery order workflows
- Repair ticket management
- Multi-project stock allocation
- Role-based access control
- Stock in/out/transfer operations
- PDF report generation
