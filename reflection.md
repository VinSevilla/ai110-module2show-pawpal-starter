# PawPal+ Project Reflection

## 1. System Design

- Three main actions needed to be performed:

1. Obtain basic user/ pet information
2. Provide user schedule/ time constraints
3. schedule tasks based on user input and constraints

- Initial brainstorms of objects and classes included:

1. Pet (attributes): name, type, age, maintenance_level (functions): add/edit pet info, view pet info
2. Task (attributes): name, duration, priority (functions): ability to add/remove, edit duration/priority
3. Schedule (attributes): time_constraints (functions): method to generate schedule based on tasks and constraints
4. User (attributes): name, user_schedule, user_pets (functions): add/edit user info, add/edit user pets

- Clarification:
- The pet class contains basic pet info and methods to manage that info. It also include maintenance level to indicate pet health and care needs.
- The task class represents individual care tasks with attributes for name, duration, and priority. It includes methods to manage tasks.
- The schedule class contains a time constraint attribute derived from the user's schedule. It has a method to generate a daily schedule based on the tasks and constraints.
- The user class contains basic information about the pet owner, as well as their schedule and pets under their care.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- The initial UML design included four main classes: Pet, Task, Schedule, and User.
  The responsibility of the Pet class was to manage pet information and indicate the maintenance level of the pet, so the user can decide what and how much care the pet needs. The Task class is responsible for representing the individual care tasks communicated by the user, communicating the duration and priority of each tasks towards the schedule. The schedule class is responsible for taking into account, the time constraints of the user and the duration of each task to generate a presentable schedule for a specific pet. The user class is responsible for managing the pet owners information including hoe many pets they have and their schedule, which is important for the task and schedule class to generate a schedule that fits the user's needs and constraints.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler places each task at the earliest open slot in priority order and never reconsiders past decisions. This means a high-priority task could block a shorter, lower-priority task from fitting — even if swapping their order would have fit both. This tradeoff is acceptable for a pet care app because daily task counts are small, priority order is what the owner cares about most, and a more complex backtracking approach would add significant code complexity for minimal real-world gain.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
