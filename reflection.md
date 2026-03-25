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
  The responsibility of the Pet class was to manage pet information and indicate the maintenance level of the pet, so the user can decide what and how much care the pet needs. The Task class is responsible for representing the individual care tasks communicated by the user, communicating the duration and priority of each tasks towards the schedule. The schedule class is responsible for taking into account, the time constraints of the user and the duration of each task to generate a presentable schedule for a specific pet. The user class is responsible for managing the pet owners information including how many pets they have and their schedule, which is important for the task and schedule class to generate a schedule that fits the user's needs and constraints.

  **b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

## The only slight modification made to the design was how the schedule and user class interacted. Initially, I wanted the user to provide their own schedule as an input for the schedule class so that the schedule class could generate a schedule based on those constraints. Instead I decided to have the user class have a function to add constraints that would be passed to the schedule class when generating a schedule. This was because it felt more intuitive for the user to directly input their constraints into the user class rather than having to create a separate schedule object just to input constraints.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers time, priority, and user preferences. I decided priority mattered the most. Although time is very critical, I believed it to be more important to ensure high priority task were scheduled first, even if it meant a less efficient schedule. For example, if a pet needs medication at a specific time, it is more important that this task would be scheduled first at the cost of having all other tasks otherwise being able to fit in a given schedule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

## The scheduler places each task at the earliest open slot in priority order and never reconsiders past decisions. This means a high-priority task could block a shorter, lower-priority task from fitting when it would still have been possible to have fit both by just swapping their order. This tradeoff seems reasonable within the scope of a pet care app because it overall keeps the logic simple and predictable. Realistically, a person would likely want to know that a high-priority task is taking up a time slot even if it means a less efficient schedule. They also still are capable of manually adjusting the schedule if they want to fit more tasks, however, fixing the schedule algorithm to consider all possible arrangements would have added unnecessary complexity.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
  I used AI as a support tool as I was designing and implementing the system. The most helpful prompts were mostly those that required explanation of concepts or code. For example, after asking AI to provide methods and functions for some of the classes, I had ask AI the reasoning and purpose behind the code to help me be more specific in future prompting and manually make certain changes. This allowed me to better understand the suggestions and make more informed decisions about which suggestions to implement and which to modify.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

## One moment where I did not accept an AI suggestion was how it handled priority and pet maintenance level. At first, the AI decided what was considered priority of a task based on the pet's maintenance level which was determined by the number of tasks that had been completed for that pet. Essentially, the more care a pet received, the higher the maintenance level of a pet (meaning its been well maintained) which automatically set proceeding task as a low priority. Practically I did not accept this suggestion because back to the medication example, if a pet needs medication regardless of how well maintained and how many task has been completed for that pet, it should be considered a high priority task. I verified this through test cases but primarily though internal logic and reasoning. After seeing the output of the schedule, I realized that the maintenance level was not a good indicator of priority and it made more sense for the user to determine themselves what is important or not.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
  I tested the scheduling logic to ensure task with higher priority were being placed earlier in the day whilst lower priority task landed in remaining free slots. I also tested that the time constraints were being respected and that tasks that could not fit within the constraints were being notified and unplaced. A third bheavior I tested was the ability to filter tasks by pet name and status, which was allowed the user to easily view and schedule tasks for a specefic pet.
  These test were important because they verified the core functionality of the app, which was to generate a schedule that respected the users pets, constraints, and priorities.

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
