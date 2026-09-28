Title: pstack gates its parallel agents behind a verification skill your project has to generate

URL Source: https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25

Published Time: 2026-09-10T14:50:29.008Z

Markdown Content:
[Build](https://theclarity.today/build)[1 publisher](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#source-comparison)3 min read Published September 10, 2026 at 7:50 AM PDT

Lauren Tan's MIT-licensed plugin routes a described task into one of 23 playbooks, but the part that decides whether any of it transfers is the per-project skill that drives the real product and recognises failure.

The Engineer · Build desk

![Image 1: Illustration accompanying pstack gates its parallel agents behind a verification skill your project has to generate](https://theclarity.today/_next/image?url=https%3A%2F%2Fmedia.theclarity.today%2Fnews%2Fheroes%2F2026-09-10%2Fbuild%2Fpstack-gates-its-parallel-agents-behind-a-verification-skill-your-project-has-2200975730-1bcbeded5775bd79.png&w=3840&q=75)

## What happened

*   Lauren Tan has open-sourced pstack, a collection of engineering skills, principles, playbooks, subagents and automations built around the way she works with coding agents.
*   The plugin is at version 0.15.1 under an MIT license, with 23 task playbooks and 23 engineering principles carried in the repo.
*   One entry command, /poteto-mode, takes a described task, picks the workflow, loads the matching playbook, builds the work sequence and calls specialised skills as it goes.
*   The playbooks are shaped by task type: a bug gets reproduction, root-cause analysis, a targeted fix and runtime verification, while a long migration is split into units that each end in a verifiable state.

Compiled by The Engineer[Something wrong?](mailto:corrections@theclarity.us)[How this is made](https://theclarity.today/methodology)

## Why it matters

*   constraint The verification loop only exists where a program can drive and inspect the running product, so debuggability of the stack now sits upstream of any agent workflow decision rather than beside it.
*   cost The MIT license removes the acquisition cost and moves the bill to the adopting team, which pays in the work of generating a project-specific verification skill and in tokens for fan-out and multi-model review.
*   decision Anyone already fanning work across agents has to decide whether to keep going before a proof loop exists, because more parallel output lands against unchanged human reading capacity.
*   precedent Shipping the judgment as readable, diffable files sets a harder bar for the next agent-workflow pitch: the argument can be had over the contents rather than the summary.

The load-bearing command here is /create-verification-skill, which gives a project its own mechanism for proving behavior [[10]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c10). Tan's working definition of verification is concrete: the agent performs the task, interacts with the actual product, inspects the result, recognises failure, tries again, and keeps going until it can demonstrate success [[11]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c11). That loop is not a prompt trick; it is a program driving your app and reading the result.

Which is where the invisible constraint sits. If the app cannot be driven and inspected by something other than a human, the skill has nothing to call, and per theneuron.ai's account Tan follows that all the way down, arguing teams should weigh their ability to debug and control an application when choosing a technical stack [[13]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c13). That sentence is easy to skip past, but it carries the argument. It says the agent workflow is downstream of an architecture decision most teams made years ago.

The adoption number is the one to be careful with. Cursor's engineering team had used Tan's personal skills 10,000 times in a single week at the point she announced open-sourcing them [[2]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c2). Spread across seven days that is roughly 1,430 invocations a day [[20]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c20). Team size is not given, so the per-engineer rate is unknown, and a usage count says nothing about defects caught. For the figure to mean anything in your shop you would need an application an agent can exercise end to end, and engineers who read the playbook rather than the diff.

The counts also need a caveat. The repo figures are 23 and 23, while the Cursor marketplace lists 47 skill entries and two specialised subagents [[5]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c5), and the explainer does not say how those sets map onto each other [[22]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c22). At version 0.15.1 [[3]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c3) that is a snapshot of a pre-1.0 plugin, not a stable inventory.

Then the ordering. Lesson 5 of Tan's guide, as theneuron.ai lays it out, is that parallelism comes after trust [[15]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c15). The tools that make parallelism easy are already in the box: /swarm splits slices of a problem across agents, /arena runs competing attempts at the same problem, /interrogate sets multiple models on a finished diff [[14]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c14). All three multiply output. Run them before the verification skill exists and you have bought more diffs against the same human reading capacity, which is the failure the writeup opens with, five agents producing code faster than anyone can read it, while every green check still raises a new question [[19]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c19).

Cost is acknowledged and, in the material supplied, unquantified: the explainer carries a section headed "Yes, this can be absurdly expensive" [[17]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c17) and the text breaks off before the numbers. Multi-model interrogation and fan-out are the obvious line items, and there is no figure here to argue with.

The repo also ships /unslop, which cleans up AI-flavored prose [[16]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c16). A project that includes a tool for the smell of its own output is at least self-aware.

The license, the file counts, and the router behaviour are documented: /poteto-mode picks the workflow, loads the playbook, builds the work sequence, and invokes skills [[7]](https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25#claim-c7). The claim underneath, that these 23 principles encode senior judgment rather than one engineer's habits, is not something this material lets you check. That test happens in a codebase that is not Cursor's.

## What to watch

*   Whether the repo's 23/23 counts and the 0.15.1 version hold, since the inventory being cited is pre-1.0.
*   The cost figures behind the explainer's "absurdly expensive" section, which is where the token bill for /arena, /swarm and /interrogate would show up.
*   A report of verification skills generated against a codebase outside Cursor's, which is the only way the 10,000-use signal transfers.

## Claim ledger

Ranked by verification strength, evidence, and original report placement.

1.   [4]

The pstack repo contains 23 task playbooks and 23 engineering principles. 
2.   [5]

The Cursor marketplace currently exposes 47 skill entries and two specialized subagents for pstack. 
3.   [17]

theneuron.ai's pstack explainer includes a section headed "Yes, this can be absurdly expensive". 
4.   [1]

pstack is Lauren Tan's open-source collection of engineering skills, principles, playbooks, subagents and automations built around the way she works with coding agents.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
5.   [3]

The current pstack plugin is version 0.15.1 under an MIT license.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
6.   [6]

The Cursor marketplace describes pstack with the slogan "if you want to go fast, go deep first".

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
7.   [7]

With /poteto-mode you describe a task, and it decides which workflow fits, loads the relevant playbook, creates the work sequence, and invokes specialized skills as needed.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
8.   [8]

A bug might trigger reproduction, root-cause analysis, a targeted fix and runtime verification; a performance problem starts by measuring current behavior; a major architecture decision can fan out across competing designs; a long migration gets divided into small units that each end in a verifiable state.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
9.   [9]

The current pstack repo includes playbooks for investigation, bug fixing, performance work, runtime forensics, refactoring, prototyping, visual parity, autonomous runs, orchestration, shipping and multi-phase projects.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
10.   [10]

/create-verification-skill gives a project its own mechanism for proving behavior.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
11.   [11]

Tan's practical definition of verification: an agent should be able to perform a task, interact with the actual product, inspect the result, recognize failure, try again, and continue until it can demonstrate success.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
12.   [13]

Tan treats a good verification skill more like internal developer infrastructure than a clever prompt, and argues teams should consider their ability to debug and control an application when choosing a technical stack.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
13.   [14]

/swarm distributes separate slices of a problem across agents, /arena produces competing attempts at the same problem, and /interrogate asks multiple models to attack a completed diff.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
14.   [15]

Lesson 5 of Tan's pstack guide, as set out by theneuron.ai, is that parallelism comes after trust.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  

16.   [18]

theneuron.ai says pstack's router-plus-specialists structure resembles ideas already seen in Claude Code's dynamic agent workflows and OpenAI's "harness engineering" approach.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
17.   [19]

The explainer opens on the failure it describes: five agents generating code faster than you can read it, with every green checkmark raising another question about whether any of it actually worked.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
18.   [21]

pstack's individual tools include /how to trace how a subsystem works, /why to reconstruct why something was built that way, /recall to recover context from previous agent sessions and /tdd to start with a failing test.

Reported Supported[View cited source](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)  
19.   [22]

The explainer gives repo counts of 23 playbooks and 23 principles alongside marketplace counts of 47 skills and two subagents without stating how the two sets map onto each other. 
20.   [2]

The Cursor engineering team had already used Lauren Tan's personal skills 10,000 times in a single week when she announced she was open-sourcing them. 
21.   [12]

Without a closed verification loop, every "autonomous" agent eventually hands the problem back to a human for inspection, and the bottleneck moves from writing the code to babysitting whatever wrote the code. 
22.   [20]

10,000 skill uses in a single week is about 1,430 invocations a day. 

## Sources

Publishers with included, body-backed reporting in this cluster.

1.   [pstack explained: Lauren Tan’s system for trustworthy AI agents](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/)
