<!--
  HOW TO EDIT THIS REPORT
  - Edit the text below like a normal document. Save (commit) on GitHub and the PDF rebuilds itself
    in a few minutes at: https://arjunbojja1.github.io/TerpBites/report/TerpBites_Findings.pdf
  - ## is a section heading, ### is a smaller heading, **bold**, - starts a bullet.
  - Tables: keep the | lines lined up the same way. In the Methods table, write the status as
    "Done: 23 responses" or "In progress" and it turns into a colored pill.
  - Charts and pictures are the lines in {{ double braces }}. Move or delete them, but don't change the
    words inside. To change chart numbers or captions, edit report/data.json.
      {{tiles}}                      the four big stat boxes
      {{charts: persona, year}}      two charts side by side (one name = one full-width chart)
      {{figure: affinity}}           the affinity diagram picture
  - Please don't use em dashes. Use commas, periods, or parentheses instead.
-->

## Introduction

TerpBites is a website idea to help University of Maryland (UMD) students find food during the short breaks between their classes. UMD has three dining halls plus a lot of cafés, food courts, and markets spread across campus. When we pulled UMD Dining's public hours for our project site, we found 32 different venues, each with its own schedule that changes by day, and some still listed as "TBD." Students usually have to check a few different places to figure out what is actually open. TerpBites would put dining hours, prices, walking time, and menus in one place so students can quickly pick somewhere to eat without being late to their next class.

## Problem statement

Students at the University of Maryland need a quick and reliable way to get affordable food on and near campus. Right now, many students deal with unreliable dining hours, a confusing campus layout, and no clear idea how long the wait or the walk will take. Because there isn't reliable information, students waste their breaks walking to places that turn out to be closed, or they end up skipping meals altogether.

## Research questions

1. **RQ1** How do UMD students currently decide where to eat between classes?
2. **RQ2** What information matters most to students when they have limited time to get food?
3. **RQ3** What problems do students run into with dining hours, prices, distance, and wait times?
4. **RQ4** How could TerpBites make finding food between classes faster and easier?

## Audiences

So far we have heard from **42 people**: **23** through our survey and **19** through in-person interviews. None of the people we interviewed took the survey, so these are two separate groups. Of the survey respondents, 22 are current UMD College Park students and 1 said they are not, so we flag that response when we compare results. We grouped everyone by living situation, since that is what separates our two draft personas.

| Audience | Who they are (from our personas) | Survey | Interviews |
|---|---|---:|---:|
| **Commuter students**<br>Persona: Maya Torres | Live off campus and are on campus for long stretches with no kitchen nearby. Usually no resident meal plan, so they pay with a card or Terrapin Express and watch prices closely. | 16 | 16 |
| **On-campus students**<br>Persona: Jordan Lee | Live in the residence halls and usually have a meal plan. Know the dining halls near their dorm but not the food near their classes, and get hungry after the dining halls close. | 7 | 3 |
| **Freshmen** (subgroup) | First-semester students who are still learning the campus. Jordan is a freshman, so this group matters for our second persona. | 3 | 3 |
| **Dining staff and local restaurants**<br>Stakeholders | UMD Dining workers and College Park businesses who see the lunch rush and would need to share hours, menus, and wait times. | 0 | 0 |
| **Total** | | **23** | **19** |

Our interviewees were 3 freshmen who live on campus, 4 juniors who live off campus, and 12 seniors who live off campus. Most survey respondents were also seniors (14 of 23). Across both methods, the audiences we have not reached well yet are **freshmen** (6 of 42) and **on-campus students** (10 of 42), and we have not talked to any **on-campus upperclassmen** in interviews. We also have not engaged our **stakeholders**, since we have not talked to any dining staff or restaurant owners yet.

## Methods

| Method | What we did | Status |
|---|---|---|
| **Online survey** | A 14-question Google Form about dining habits: class year, living situation, how often students buy food between classes, how far they will walk, how often they skip meals, what matters when choosing, where they get information, lines, closures, prices, and what feature would help most. Q14 was open-ended: "If you could improve one thing about getting food on or near campus between classes, what would it be?" | Done: 23 responses |
| **Dining data review** | We pulled UMD Dining's public hours for every venue and the dining hall menus, and mapped each venue to its building so we could estimate walk times. This showed how much hours vary by venue and day. | Done |
| **Interviews** | Short in-person interviews with 19 UMD students (none of whom took the survey) using our interview guide, which has warm-up, general, and follow-up questions tied to our four research questions. We did not record the interviews or take notes during them, so we wrote up the main patterns afterward from memory. Because of that, we report what most interviewees said as a group, not individual quotes or exact counts. | Done: 19 interviews |
| **Contextual observation** | We wrote an observation guide using the AEIOU framework (Activities, Environments, Interactions, Objects, Users). Each member will observe one food spot during lunch: the Stamp food court, Yahentamitsi, South Campus Dining Hall, 251 North, the Kirwan food court, and Footnotes in McKeldin. | In progress |
| **Synthesis** | Affinity diagramming of the survey responses, then a 10+10 brainstorming session and We Believe statements to turn what we learned into features and testable assumptions. | Done |

This draft combines the survey, our first round of interviews, and the dining data. Our contextual observations are not finished yet. For our next round of interviews we plan to take notes during each one so we can report individual responses and quotes.

## Analysis

### Quantitative analysis

For each multiple choice question we counted the responses and calculated percentages out of all 23 respondents. Because we only have the Google Forms summary, we did not cross-tabulate answers by persona group yet. Comparing commuters and on-campus students is one of our next analysis steps.

{{tiles}}

{{charts: persona, year}}

{{charts: skipped}}

{{charts: factor, walk}}

{{charts: info, line}}

{{charts: feature}}

### Qualitative analysis

**Interviews.** After the interviews, we wrote down the patterns that came up the most and compared each one to our survey results and affinity themes. The interviews mostly backed up the survey and added detail about what happens once students get to a food spot.

{{charts: interviews}}

| What interviewees told us | Matching survey evidence | Theme |
|---|---|---|
| They usually spend **20+ minutes** finding somewhere to eat, or, once they get somewhere, finding something they actually want to eat. | 87% skipped or delayed a meal because of time; 52% go somewhere else when the line is long. | Time is the real limit |
| They decide where to eat based on **how close a place is** to where they are and **what's on the menu**. | Distance was the top factor (39%); prices and menus tied for most useful feature (35%). | Distance and campus layout; Knowing before going |
| What goes wrong: **distance, price, lines, and menu offerings**. | 74% say price matters moderately or very much; 48% hit long lines sometimes or often. | All four themes |
| They **don't check much** before going. Some check menus or a map for the closest dining hall or restaurant. | 65% use Google Maps; only 9% use the UMD Dining website. | Knowing before going |

**Survey affinity diagram.** We put each answer to the open-ended question (Q14) on its own sticky note, splitting answers that had more than one idea, and added notes for the key survey numbers. We grouped similar notes without naming the groups at first, then labeled each group from a student's point of view. We ended with eight groups, which we combined into four themes and tagged with the research questions they help answer.

{{figure: affinity}}

| Theme | Groups inside it | What students said | RQ |
|---|---|---|---|
| **Time is the real limit** | I never know how long the line will be; When time runs out, I skip or delay meals | "knowing if there's going to be line beforehand," "crowd meter/ wait time," "Order ahead and pay in person" | RQ1, RQ3 |
| **Distance and campus layout** | I can only walk a few minutes; Food is bunched in a couple of spots | "there are 2 main areas to get food on campus if you don't have a dining plan," "Having more options spread out throughout campus" | RQ1, RQ3 |
| **Knowing before going** | I want to see the menu before I go; Info is scattered, so closures surprise me | "others I dont really know till I get there... I just wasted a break to eat nothing" | RQ2, RQ4 |
| **Cost and food quality** | Price (and how I can pay) matters; I want healthier, more varied food | "a lot of places in STAMP do not take dining dollars," "Better and healthier food options" | RQ3 |

## Conclusions

### What we learned

- **Time is the main problem, not food.** 87% of survey respondents skipped or delayed a meal in the last two weeks because of time, and the most common open-ended request was knowing about lines or wait times before walking over. Interviewees said they usually spend 20 or more minutes finding somewhere to eat or something they want once they get there (RQ3).
- **Students pick by distance and menu.** Distance is the top factor in the survey (39%), and almost half will only walk 5 to 9 minutes. Interviewees also decided based on how close a place is and what's on the menu, and survey answers pointed out that food is concentrated at the Stamp and Kirwan (RQ1).
- **The information exists but students don't use it.** 65% use Google Maps and only 9% use the UMD Dining website, where the official hours are, and interviewees said they don't check much before going. 48% have found a place unexpectedly closed, yet nobody named hours as their top factor, which suggests students assume places are open until they aren't (RQ2).
- **Price, lines, and menus are the main things that go wrong.** Interviewees named distance, price, lines, and menu offerings. In the survey, 74% say price affects their choice moderately or very much, and one student pointed out that many places in the Stamp don't accept Dining Dollars (RQ3).
- **Students want three things from TerpBites:** walking distance and prices/menus (35% each) and estimated wait times (26%) (RQ4).

### Unanswered questions

- How long do lines actually take at different spots and times? The 20+ minutes interviewees described is their own estimate, so our observations should measure it.
- Do commuters and on-campus students behave differently? Only 10 of the 42 people we heard from live on campus, and all 3 on-campus interviewees were freshmen, so we need more on-campus students.
- Why do students rely on Google Maps over the UMD Dining site, and would they trust TerpBites' hours instead? We need to ask this directly and take notes in our next interviews.
- Would dining staff and restaurants be able or willing to share wait times and menus? We have not talked to any stakeholders yet.

### How this informs brainstorming and prototyping

These findings directly shaped our 10+10 brainstorming. Out of 10 feature ideas, we voted for **real-time dining hours**, a **break length filter**, and **current location**, because they line up with the time, closure, and distance problems from the survey and interviews. The interviews also showed that menus matter once students arrive, which supports adding menus to the break length filter results. We wrote a We Believe statement for each one. For example, we believe a break length filter for UMD students with busy schedules will help them find a place where they can fit in a meal, and we will know we are right if users can finish a meal within the break time they set. Our next steps are to finish our observations, do a second round of interviews with notes, update the Maya and Jordan personas (commuters were a bigger group than we expected), and build a clickable prototype that combines all three features into one flow so we can test our We Believe statements with real students.
