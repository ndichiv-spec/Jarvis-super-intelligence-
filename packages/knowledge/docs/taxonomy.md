# Knowledge Taxonomy

## Classification Dimensions

Knowledge is classified across the following orthogonal dimensions:

| Dimension     | Values                                    | Description                         |
|---------------|-------------------------------------------|-------------------------------------|
| Domain        | Free-form string (e.g., engineering, finance, medicine) | Broad knowledge area  |
| Topic         | Free-form string (e.g., microservices, derivatives)    | Specific subject        |
| Category      | Free-form string (e.g., tutorial, reference, spec)     | Content type           |
| Importance    | Low, Normal, High, Critical               | Priority level                    |
| Sensitivity   | Low, Internal, Confidential, Restricted   | Confidentiality level             |
| Visibility    | Private, Workspace, Project, Enterprise, Public | Access scope                |
| Language      | IETF language tag (e.g., en, fr, zh)      | Content language                 |
| Workspace     | Free-form string                          | Logical workspace                 |
| Project       | Free-form string                          | Logical project                   |
| Tags          | Set of free-form strings                  | Arbitrary keywords                |

## Importance Levels

| Level    | Description                | Typical Use Case              |
|----------|----------------------------|--------------------------------|
| LOW      | Optional reference         | General reading                |
| NORMAL   | Standard knowledge         | Documentation                  |
| HIGH     | Important knowledge        | Architecture decisions         |
| CRITICAL | Foundational knowledge     | Security policies, compliance  |

## Sensitivity Levels

| Level        | Description            | Example                         |
|--------------|------------------------|---------------------------------|
| LOW          | Public information     | Public documentation            |
| INTERNAL     | Internal use only      | Engineering wiki                |
| CONFIDENTIAL | Sensitive information  | Business strategy               |
| RESTRICTED   | Highly restricted      | Trade secrets, legal documents  |

## Visibility Levels

| Level      | Scope                                      |
|------------|--------------------------------------------|
| PRIVATE    | Owner only                                 |
| WORKSPACE  | All users in the same workspace            |
| PROJECT    | All users assigned to the project          |
| ENTERPRISE | All authenticated enterprise users         |
| PUBLIC     | Unauthenticated external access (future)   |

## Relationship Types

| Type          | Description                                  |
|---------------|----------------------------------------------|
| REFERENCE     | General reference link                       |
| DEPENDS_ON    | Target is a dependency of source             |
| DERIVED_FROM  | Source was derived from target               |
| SUPERSEDES    | Source replaces target (newer version)       |
| EXPLAINS      | Source provides explanation for target       |
| RELATED_TO    | Bidirectional association                    |
| VERSION_OF    | Source is a version of target                |
| PARENT        | Source is a parent of target                 |
| CHILD         | Source is a child of target                  |
| CITATION      | Source cites target                          |

## Source Types

| Type                | Example                      |
|---------------------|------------------------------|
| DOCUMENTATION       | API docs, user guides        |
| BOOK                | Technical or academic books  |
| RESEARCH_PAPER      | Academic publications        |
| SPECIFICATION       | Protocol or interface specs  |
| MANUAL              | Operations manuals           |
| USER_DOCUMENT       | User-provided content        |
| POLICY              | Organizational policies      |
| WEB_RESOURCE        | Online articles, blogs       |
| ENTERPRISE_REPOSITORY | Internal enterprise systems |
| OTHER               | Uncategorized                |
