# BMad Method Development Plan: AI Workflow Builder

**Project:** AI Workflow Builder  
**Date Created:** October 3, 2025  
**Plan Version:** 1.0  
**Current Status:** Planning Complete - Ready for Development Phase

## Executive Summary

This document provides the complete sequential roadmap for developing the AI Workflow Builder using the BMad Method. The planning phase has been completed with all required artifacts. This plan covers the transition from planning to development execution, including specific commands, expected outcomes, and quality checkpoints.

## Phase 0: Discovery, Research & UX Validation (Pre-Build Enablement)

Purpose: Establish validated problem understanding, UX foundations, and feasibility signals before sharding and story drafting. Skip only if a prior validated PRD, UX Spec, and research baseline already exist with no material deltas.

### Step 0.1: Problem & Opportunity Research (Analyst)

**When:** New domain, pivot, unclear user pain, or competitive ambiguity.

**Commands (examples):**

```bash
*agent analyst
*brainstorm "workflow authoring pain points"
*perform-market-research
*create-competitor-analysis
```

**Outputs:** Market/competitor snapshot, clarified user segments & JTBD, refined problem framing feeding Project Brief / PRD goals.

**Success Criteria:**

- [ ] Primary user segments & top JTBD articulated
- [ ] 3–5 differentiators vs. key competitors captured
- [ ] Risks / open questions logged into PRD risks section

### Step 0.2: Experience Modeling & Early UX Architecture (UX Expert)

**When:** Prior to (or parallel with) epic definition; whenever major interaction paradigms are novel.

**Commands:**

```bash
*agent ux-expert
*generate-ui-prompt
```

**Activities:** Core user flows, preliminary IA, component taxonomy (atomic → composite), accessibility intents, responsive breakpoints.

**Success Criteria:**

- [ ] MVP happy-path flows mapped
- [ ] Initial component taxonomy drafted
- [ ] Accessibility & responsive constraints noted

### Step 0.3: Feasibility & Constraint Scan (Analyst + Architect as needed)

Identify technical assumptions, integration constraints, performance / scale concerns, and build-vs-buy candidates.

**Outputs:** Assumption list, integration risk notes, flagged high-risk areas for early architecture scrutiny.

### Step 0.4: UX Prompt & Design Asset Generation (Optional)

Use UX Expert to create master AI generation prompt for rapid wireframes / mockups.

**Command:**

```bash
*agent ux-expert
*generate-ui-prompt
```

### Step 0.5: Alignment & Handover

Analyst synthesizes research + UX Expert flows → Product Owner updates PRD Epics & UI/UX Spec; Scrum Master prepares for story drafting. If major uncertainty remains, loop 0.1–0.3 selectively.

---

## Current Project State

### ✅ Completed Planning Artifacts
- **Project Brief:** `docs/project-brief.md` - Vision, goals, and scope
- **PRD:** `docs/PRD.md` - Detailed requirements and 4 epics with stories
- **Architecture:** `docs/Architecture.md` - Complete technical specification
- **UI/UX Spec:** `docs/UI_UX-Specification.md` - Frontend design blueprint
- **BMad Configuration:** `.bmad-core/core-config.yaml` - Development settings

### 📋 Epic Overview
- **Epic 1:** Foundation & Core Generation Engine (6 stories)
- **Epic 2:** User & Workflow Persistence (3 stories)  
- **Epic 3:** Full Two-Way Interactivity (3 stories)
- **Epic 4:** Advanced Execution & Stateful Debugging (3 stories)
- **Total:** 15 stories across 4 epics

## Phase 1: Document Preparation & Sharding

### Step 1.1: Shard the PRD Document
**Purpose:** Break large PRD into manageable epic files for story creation

**Command:**
```
*agent po
*shard-doc docs/PRD.md docs/prd
```

**Expected Outcome:**
- Creates `docs/prd/` folder with individual epic files
- Files: `epic-1.md`, `epic-2.md`, `epic-3.md`, `epic-4.md`, `index.md`
- Each epic file contains specific stories and requirements

**Success Criteria:**
- [ ] All 4 epic files created successfully
- [ ] Epic files contain complete story definitions
- [ ] Index file provides navigation to all epics

**Analyst / UX Hooks:**
- Analyst: Post-shard scope audit vs. Phase 0 research (detect scope drift).
- UX Expert: Flag UI-heavy epics missing interaction narrative or accessibility notes.

### Step 1.2: Shard the Architecture Document
**Purpose:** Create focused architecture files for development reference

**Command:**
```
*agent po
*shard-doc docs/Architecture.md docs/architecture
```

**Expected Outcome:**
- Creates `docs/architecture/` folder with technical specifications
- Key files: `tech-stack.md`, `unified-project-structure.md`, `coding-standards.md`
- Files referenced in `devLoadAlwaysFiles` configuration

**Success Criteria:**
- [ ] Architecture files created and properly organized
- [ ] Tech stack specifications are clear and actionable
- [ ] Project structure guidelines are detailed

### Step 1.3: Validate Document Alignment
**Purpose:** Ensure all planning documents are consistent and complete

**Command:**
```
*agent po
*execute-checklist po-master-checklist
```

**Expected Outcome:**
- Comprehensive validation report of all planning artifacts
- Identification of any gaps or inconsistencies
- Approval to proceed with development

**Success Criteria:**
- [ ] All checklist items pass or have documented exceptions
- [ ] No critical alignment issues identified
- [ ] Documents provide sufficient context for development

## Phase 2: Story Creation & Development Cycle

### Step 2.1: Create First Story (Epic 1, Story 1.1)
**Purpose:** Generate detailed implementation-ready story from sharded epic

**Command:**
```
*agent sm
*draft
```

**Expected Outcome:**
- Creates `docs/stories/1.1.story.md` - "Project Scaffolding & Setup"
- Story includes: requirements, acceptance criteria, technical context, tasks
- Story status: "Draft"

**Next Step:**
- Manually review the generated story in `docs/stories/`
- Update the story status from "Draft" to "Approved" to signal it is ready for development.

**Success Criteria:**
- [ ] Story file created with complete technical context
- [ ] All acceptance criteria clearly defined
- [ ] Implementation tasks are sequential and actionable
- [ ] Dev Notes section contains architecture references

### Step 2.2: Pre-Development Quality Assurance (Recommended)

**Purpose:** Identify risks and define a test strategy *before* development begins to ensure a higher quality result. This is highly recommended for complex or high-risk stories.

**Commands:**
```bash
# 1. RISK ASSESSMENT (Run FIRST for complex stories)
*agent qa
*risk 1.1

# 2. TEST DESIGN (Run SECOND to guide implementation)
*agent qa
*design 1.1
```

**Expected Outcomes:**

- **Risk Assessment:**
    - Creates a risk profile document: `docs/qa/assessments/1.1-risk-{date}.md`
    - Includes a risk matrix, probability/impact analysis, and mitigation strategies.
- **Test Design:**
    - Creates a test design document: `docs/qa/assessments/1.1-test-design-{date}.md`
    - Includes test scenarios, test level recommendations (unit/integration/e2e), and prioritization.

**Success Criteria:**

- [ ] Risks are identified and assessed with clear mitigation plans.
- [ ] A comprehensive test strategy is in place to guide development and testing.

### Step 2.3: Validate Story (Recommended for Complex Stories)

**Purpose:** Ensure story has sufficient context for successful implementation

**Command:**
```
*agent po
*validate-story-draft 1.1
```

**Expected Outcome:**

- Comprehensive story validation report
- Identification of missing information or context
- Recommendations for story improvements

**Success Criteria:**

- [ ] Story validation passes or issues are addressed
- [ ] All technical dependencies are identified
- [ ] Implementation approach is clear and feasible

## Phase 3: Implementation Loop (Repeat for Each Story)

### Step 3.1: Story Implementation
**Purpose:** Complete all development tasks for the story.

**Command:**
```
*agent dev
*develop-story
```

**Implementation Process:**
1. The Dev agent reads the story and loads the required architecture files.
2. It implements the tasks sequentially, including writing tests.
3. It runs validations like linting and tests.
4. Upon completion, it updates the story with notes and a list of modified files.
5. The story status is set to "Ready for Review".

**Expected Outcome:**
- All story tasks completed and marked with `[x]`.
- Complete test coverage for new functionality.
- Story status: "Ready for Review".
- Updated Dev Agent Record with implementation details.

**Success Criteria:**
- [ ] All acceptance criteria are met.
- [ ] All tasks are completed and tested.
- [ ] Code follows project standards.
- [ ] No linting errors or test failures.

### Step 3.2: Mid-Development QA Checks (Developer Self-Service)
**Purpose:** Validate quality during the development process as a self-service check.

**Commands:**
```bash
# 1. REQUIREMENTS TRACING (Verify coverage mid-development)
*agent qa
*trace 1.1

# 2. NFR VALIDATION (Check quality attributes)
*agent qa
*nfr 1.1
```

**Expected Outcome:**
- **Requirements Traceability:** A report (`docs/qa/assessments/1.1-trace-{date}.md`) ensuring all acceptance criteria have corresponding tests.
- **NFR Assessment:** An assessment (`docs/qa/assessments/1.1-nfr-{date}.md`) checking for security, performance, reliability, and maintainability.
- Early identification of any quality gaps.

**Success Criteria:**
- [ ] All requirements have corresponding tests.
- [ ] NFR standards are met or gaps are documented.
- [ ] Quality issues are addressed during development.

### Step 3.3: Quality Assurance Review (Required)
**Purpose:** A comprehensive quality assessment and active improvement by the Test Architect (QA Agent).

**Prerequisite:** All tests pass locally; lint and type checks are clean.

**Command:**
```bash
*agent qa
*review 1.1
```

**Review Process:**
1. **Deep Code Analysis:** Checks architecture compliance, code quality, and security.
2. **Active Refactoring:** Improves code directly when safe.
3. **Test Validation:** Assesses test coverage and quality.
4. **Quality Gate Decision:** Issues a `PASS`, `CONCERNS`, `FAIL`, or `WAIVED` status.

**Expected Outcome:**
- A `QA Results` section is added to the story file.
- A quality gate file is created: `docs/qa/gates/1.1-{slug}.yml`.
- Code improvements are applied directly by the agent.
- A clear gate status with rationale is provided.

**Success Criteria:**
- [ ] Quality gate status is `PASS` or has acceptable `CONCERNS`.
- [ ] All high-severity issues are addressed.
- [ ] Code quality improvements are applied.
- [ ] Test coverage meets project standards.

### Step 3.4: Address QA Feedback (If Needed)
**Purpose:** Systematically resolve issues identified in the QA review.

**Command:**
```bash
*agent dev
*review-qa
```

**Expected Outcome:**
- All findings from the QA review are addressed.
- The story is updated with details of the fixes.
- Test runs and linting are clean.

**Success Criteria:**
- [ ] All `FAIL` items are resolved.
- [ ] `CONCERNS` items are addressed or documented as accepted risk.
- [ ] The story is ready for final validation.

### Step 3.5: Update Quality Gate (As Needed)
**Purpose:** Update the quality gate decision after fixes have been applied.

**Command:**
```bash
*agent qa
*gate 1.1
```

**Expected Outcome:**
- The quality gate file (`docs/qa/gates/1.1-{slug}.yml`) is updated with the new status.
- Documents what was fixed and what, if anything, was waived.

**Success Criteria:**
- [ ] The final gate status accurately reflects the story's quality.

### Step 3.6: Final Validation & Story Completion
**Purpose:** Complete the story and prepare for the next iteration.

**Process:**
1. Verify all tests pass: `deno test -A`
2. Verify clean linting: `deno lint`  
3. **CRITICAL:** Commit all changes before proceeding
4. Mark story status as "Done"

**Success Criteria:**
- [ ] All validation checks pass
- [ ] Changes are committed to version control
- [ ] Story marked as complete
- [ ] Ready to proceed to next story

## Phase 4: Epic & Project Management

### Step 4.1: Epic Progress Tracking
**Purpose:** Monitor overall epic completion and plan next steps

**Process:**
1. Review completed stories in current epic
2. Identify next story in sequence
3. Assess if epic completion criteria are met

**Epic 1 Story Sequence:**
- 1.1: Project Scaffolding & Setup
- 1.2: Implement NLP to Python Generation API
- 1.3: Implement Workflow Visualization API  
- 1.4: Build Core UI Layout
- 1.5: Implement Secure Execution Engine
- 1.6: Implement Real-time Event Streaming

### Step 4.2: Epic Completion Validation
**Purpose:** Ensure epic delivers complete value before moving to next epic

**Command:**
```
*agent po
*execute-checklist po-master-checklist
```

**Expected Outcome:**
- Epic completion validation
- Integration testing results
- Readiness assessment for next epic

**Success Criteria:**
- [ ] All epic stories completed successfully
- [ ] Epic acceptance criteria met
- [ ] System integration validated

### Step 4.3: Project Milestone Reviews
**Purpose:** Validate overall project health and alignment

**Process:**
1. Review overall project progress
2. Validate architecture assumptions
3. Update technical preferences based on learned patterns
4. Plan next epic execution

## Quality Standards & Best Practices

### Code Quality Requirements
- **Test Coverage:** Minimum 80% for new code
- **Linting:** Zero linting errors before story completion
- **Type Safety:** Full TypeScript compliance
- **Documentation:** All public APIs documented

### BMad Process Standards
- **Story Isolation:** Each story should be independently completable
- **Quality Gates:** All stories must pass QA review or have documented waivers
- **Version Control:** Commit changes after each completed story
- **Context Management:** Keep architecture files lean and focused

### Specialized Agent Roles

While the core workflow revolves around the PO, SM, Dev, and QA agents, BMad also includes specialized agents for specific tasks. These agents can be invoked as needed to provide expert input.

- **Analyst Agent (`*agent analyst`):** Use this agent for in-depth research, data analysis, and to gain insights into market trends, competitor features, or technical feasibility. This is most valuable during the initial planning and discovery phases.
- **UX-Expert Agent (`*agent ux-expert`):** This agent specializes in user experience and interface design. Use it to refine UI/UX specifications, review wireframes, and ensure the application is intuitive and user-friendly. It is a valuable resource during the design phase and for stories with significant UI components.

### Risk Management
- **High-Risk Stories:** Always run risk assessment and test design
- **Integration Points:** Extra QA attention for cross-system integrations
- **Security Critical:** Additional security review for authentication and execution sandbox

## Success Metrics

### Development Velocity
- **Target:** Complete 1-2 stories per week
- **Epic Completion:** 3-4 weeks per epic
- **MVP Timeline:** 12-16 weeks total

### Quality Metrics
- **Gate Pass Rate:** >80% of stories pass QA on first review
- **Bug Escape Rate:** <5% of completed stories require post-completion fixes
- **Technical Debt:** Maintain architecture compliance score >90%

### User Value Delivery
- **Epic 1:** Core functionality demonstrable
- **Epic 2:** User can save and manage workflows
- **Epic 3:** Full interactive editing capability
- **Epic 4:** Production-ready with debugging

## Risk Mitigation Strategies

### Technical Risks
- **Complex Synchronization:** Implement Epic 3 with extra QA rigor
- **Security Sandbox:** Extensive testing for Epic 1, Story 1.5
- **Performance:** Monitor NFRs throughout development

### Process Risks
- **Story Scope Creep:** Strict adherence to acceptance criteria
- **Quality Shortcuts:** No skipping QA reviews for time pressure
- **Context Loss:** Regular architecture document updates

## Next Steps

### Immediate Actions (Next 1-2 Days)
1. **Execute Step 1.1:** Shard PRD document
2. **Execute Step 1.2:** Shard Architecture document  
3. **Execute Step 1.3:** Validate document alignment
4. **Execute Step 2.1:** Create first story (1.1)

### Week 1 Goals
- Complete document sharding and validation
- Create and validate first 2-3 stories
- Begin implementation of Epic 1, Story 1.1

### Month 1 Goals  
- Complete Epic 1 (Foundation & Core Generation Engine)
- Demonstrate core workflow generation capability
- Validate technical architecture assumptions

## Appendix A: Command Reference

### Essential BMad Commands
```bash
# Agent Activation
*agent po          # Product Owner
*agent sm          # Scrum Master  
*agent dev         # Developer
*agent qa          # Quality Assurance
*agent architect   # System Architect
*agent analyst     # Analyst Agent
*agent ux-expert   # UX Expert Agent

# Document Management
*shard-doc {source} {destination}    # Break large docs into smaller files
*doc-out                             # Output current document

# Story Management
*draft                               # Create next story (SM)
*validate-story-draft {story}        # Validate story completeness (PO)
*develop-story                       # Implement story (Dev)

# Quality Assurance
*risk {story}                        # Risk assessment
*design {story}                      # Test design  
*trace {story}                       # Requirements traceability
*nfr {story}                         # Non-functional requirements
*review {story}                      # Comprehensive QA review
*gate {story}                        # Update quality gate

# Process Management
*execute-checklist {checklist}       # Run validation checklist
*help                                # Show available commands
*status                              # Show current context
```

### File Path Conventions
```
docs/prd/epic-{n}.md                           # Sharded epic files
docs/architecture/{component}.md               # Architecture components
docs/stories/{epic}.{story}.story.md           # Story files
docs/qa/assessments/{story}-{type}-{date}.md   # QA assessments
docs/qa/gates/{story}-{slug}.yml               # Quality gates
```

## Appendix B: Troubleshooting Guide

### Common Issues & Solutions

**Story Creation Fails:**
- Verify PRD is properly sharded
- Check that epic files contain complete story definitions
- Ensure architecture files are accessible

**QA Review Fails:**
- Review acceptance criteria completeness
- Verify all tasks are implemented and tested
- Check code quality standards compliance

**Development Blocked:**
- Verify all required architecture files are loaded
- Check that story has sufficient technical context
- Validate development environment setup

**Quality Gate Concerns:**
- Address high-severity issues first
- Document any accepted risks with rationale
- Ensure test coverage meets project standards

---

**Document Status:** Ready for Execution  
**Next Action:** Execute Phase 1, Step 1.1 - Shard PRD Document  
**Responsibility:** Product Owner Agent (`*agent po`)