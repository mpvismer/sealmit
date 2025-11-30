# SEALMit Testing Strategy

## 1. Overview

This document outlines the testing architecture for the SEALMit project. The strategy prioritizes high-level verification and low maintenance over granular unit testing.

## 2. Architecture Layers

| Layer | Scope | Approach | Location |
|-------|-------|----------|----------|
| **AI-Agent E2E** | Ad-hoc user flows, Exploratory testing | **Dynamic AI Agent** (LLM + Playwright) | `scripts/ai_tester.py` |
| **Frontend Integration** | Design compliance, Component interactions | **Vitest** + **React Testing Library** | `frontend/src/tests/integration/` |
| **Backend Integration** | API endpoints, Data persistence | **Pytest** + **TestClient** | `backend/tests/integration/` |

> **Note**: Unit testing is explicitly excluded to reduce maintenance overhead.

---

## 3. Detailed Architecture

### 3.1 AI-Agent E2E Testing (Dynamic)

**Approach**: Ad-hoc, exploratory testing performed dynamically by a Human or AI Agent.

*   **No Persistent Scripts**: We do not maintain E2E test files.
*   **Execution**: Testing is performed on-demand either by a Human or an AI Agent, where effectively the plan and tests are created each time that testing is performed.

### 3.2 Frontend Integration Testing

Verifies that the frontend implementation complies with `DETAILED_DESIGN_FRONTEND.md`.

*   **Tool**: **Vitest** + **React Testing Library**.
*   **Focus**:
    *   **Design Compliance**: Verify that pages contain the components specified in the design (e.g., "ProjectDashboard should have tabs for Requirements, Risks, Verification").
    *   **Routing & Navigation**: Verify that clicking links navigates to the correct routes defined in the design.
    *   **Data Flow**: Verify that forms submit the correct payloads to the (mocked) API.
*   **Example**:
    ```jsx
    test('ProjectDashboard complies with design structure', async () => {
      render(<ProjectDashboard />);
      // Verify tabs defined in Design Section 5.3
      expect(screen.getByText('Requirements')).toBeInTheDocument();
      expect(screen.getByText('Risks')).toBeInTheDocument();
      expect(screen.getByText('Verification')).toBeInTheDocument();
    });
    ```

### 3.3 Backend Integration Testing

Verifies that the API behaves as expected according to `DETAILED_DESIGN_BACKEND.md`.

*   **Tool**: **Pytest** + **FastAPI TestClient**.
*   **Focus**:
    *   **API Contract**: Verify endpoints return the structures defined in the design.
    *   **Persistence**: Verify data is correctly saved to the Git storage (mocked or temp dir).
    *   **Error Handling**: Verify 400/404/500 responses as documented.

---

## 4. Implementation Plan

### Phase 1: Backend Integration
1.  Set up `pytest` environment.
2.  Migrate `verify_backend.py` logic to a proper Pytest suite `backend/tests/integration/`.

### Phase 2: Frontend Integration
1.  Set up `vitest` environment.
2.  Create integration tests for `ProjectDashboard` and `RequirementsView` to verify design compliance.
