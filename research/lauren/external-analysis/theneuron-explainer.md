Title: pstack explained: Lauren Tan’s system for trustworthy AI agents

URL Source: https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/

Published Time: 2026-09-10T12:23:28.571Z

Markdown Content:
There is an awkward stage in learning to code with AI where everything suddenly feels possible, right before everything starts breaking.

One agent writes the feature. Another reviews it. A third agent gets a separate branch. Soon you have five agents generating code faster than you can read it, and every green checkmark creates another question: **Did any of this actually work?**

Lauren Tan’s answer is [pstack](https://github.com/cursor/plugins/tree/main/pstack), an open-source collection of engineering skills, principles, playbooks, subagents, and automations built around the way she works with coding agents. The Cursor engineering team had already used her personal skills **10,000 times in a single week** when she announced she was open-sourcing them.

The [Cursor marketplace describes pstack](https://cursor.com/marketplace/cursor/pstack) with a wonderfully backwards-sounding slogan: “if you want to go fast, go deep first.” The current plugin is version 0.15.1 under an MIT license. Its repo contains 23 task playbooks and 23 engineering principles, while the marketplace currently exposes 47 skill entries and two specialized subagents.

Those numbers make pstack sound like a giant prompt library.

That undersells it.

**pstack is Lauren’s attempt to turn the parts of software engineering that happen inside a senior engineer’s head into machinery an agent can repeatedly execute.**

And the most important piece of that machinery is proof.

*   [What pstack actually is](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#what-pstack-actually-is)
*   [Lesson #1: verification is infrastructure](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#lesson-1-verification-is-infrastructure)
*   [Lesson #2: give the agent a map of reality](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#lesson-2-give-the-agent-a-map-of-reality)
*   [Lesson #3: context engineering becomes the human’s job](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#lesson-3-context-engineering-becomes-the-humans-job)
*   [Lesson #4: plan by touching reality](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#lesson-4-plan-by-touching-reality)
*   [Lesson #5: parallelism comes after trust](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#lesson-5-parallelism-comes-after-trust)
*   [Yes, this can be absurdly expensive](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#yes-this-can-be-absurdly-expensive)
*   [The most useful part of pstack may be the parts you steal](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#the-most-useful-part-of-pstack-may-be-the-parts-you-steal)
*   [Where pstack goes from here](https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/#where-pstack-goes-from-here)

## What pstack actually is

Most of the time, you start with one command:

`/poteto-mode`

You describe a task. Poteto Mode decides which workflow fits, loads the relevant playbook, creates the work sequence, and invokes specialized skills as needed.

A bug might trigger reproduction, root-cause analysis, a targeted fix, and runtime verification. A performance problem starts by measuring the current behavior. A major architecture decision can fan out across competing designs. A long migration gets divided into small units that each end in a verifiable state.

The current repo includes playbooks for investigation, bug fixing, performance work, runtime forensics, refactoring, prototyping, visual parity, autonomous runs, orchestration, shipping, multi-phase projects, and more.

Underneath those playbooks sit individual tools:

*   `/how` traces how a subsystem works.
*   `/why` reconstructs why something was built that way.
*   `/recall` recovers context from previous agent sessions.
*   `/teach` combines research into an explanation a human can understand.
*   `/architect` works through types, interfaces, and module structure.
*   `/arena` produces competing attempts at the same problem.
*   `/swarm` distributes separate slices of a problem across agents.
*   `/interrogate` asks multiple models to attack a completed diff.
*   `/tdd` starts with a failing test.
*   `/create-verification-skill` gives a project its own mechanism for proving behavior.
*   `/unslop` cleans up AI-flavored prose.
*   `/bro` restates a complicated answer in plain English.

Poteto Mode means you generally do not need to remember that catalog yourself. It routes the work.

That router-plus-specialists structure should look familiar to anyone following agent development. We’ve already seen similar ideas in [Claude Code’s dynamic agent workflows](https://www.theneuron.ai/explainer-articles/claude-code-dynamic-workflows-explained-claude-can-now-build-its-own-workflow-around-a-task/) and [OpenAI’s “harness engineering” approach](https://www.theneuron.ai/explainer-articles/openais-harness-engineering-playbook-how-to-ship-1m-lines-of-code-without-writing-any/).

pstack’s distinctive contribution is the philosophy governing those workers.

## Lesson #1: verification is infrastructure

Lauren starts [Part 1 of her pstack guide](https://x.com/poteto/status/2094457600259842065) with verification because everything else depends on it.

Her definition is practical: an agent should be able to perform a task, interact with the actual product, inspect the result, recognize failure, try again, and continue until it can demonstrate success.

That closes the loop.

Without it, every “autonomous” agent eventually hands the problem back to a human for inspection. Your bottleneck moves from writing the code to babysitting whatever wrote the code.

Lauren treats a good verification skill more like internal developer infrastructure than a clever prompt. She goes as far as arguing that teams should consider their ability to debug and control an application when choosing a technical stack.

Her `/create-verification-skill` turns that idea into something concrete.

For a web or Electron application, an agent might get a small CLI capable of opening the application, navigating it, clicking controls, taking accessibility snapshots, recording traces, capturing screenshots, changing feature flags, and waiting for the interface to settle.

Lauren calls the broader principle **“Build the Lever.”**

Repeated manual work should become a tool the agent can invoke. A CLI command consumes less context than repeatedly generating a custom script, gives every agent the same interface, and creates something humans can rerun when they need to audit the result.

That idea runs throughout the current pstack principles. The repo tells agents to build a script, codemod, generator, or reusable skill when it can replace repeated handwork. It separately requires completed tasks to be verified against the real artifact rather than against compilation, self-reporting, or another proxy.

This is one of the strongest ideas in pstack because it changes what “done” means.

**The agent has to produce evidence.**

## Lesson #2: give the agent a map of reality

Verification creates another problem.

An agent cannot efficiently test a large product if every run begins by rediscovering where every feature lives.

Lauren’s solution is a **Feature Map**, a set of compact references describing each user-facing feature, how to reach it, how to control it, and any traps an agent should know about.

She describes it as **“materialized memory.”**

Instead of stuffing the entire history of the product into every prompt, you maintain a compact representation of what exists now. The application itself remains the source of truth; the Feature Map becomes a cheaper index into it.

The clever part is maintenance.

pstack’s `/maintain-verification-skill` refreshes that map as the product changes. Lauren recommends running it at least daily so the agent’s model of the product does not slowly diverge from the product itself.

That sounds like a small implementation detail. It points toward a much larger shift.

For years, teams have written documentation primarily for humans. Agent-heavy teams increasingly need **machine-usable operational memory**: compact maps, reproducible commands, explicit interfaces, historical records, and verification tools that help an agent regain competence after its context disappears.

We saw the same pattern when we [dug into Claude Code’s architecture](https://www.theneuron.ai/explainer-articles/anthropic-leaks-claude-code-a-literal-blueprint-for-ai-coding-agents/): the model gets most of the attention, while memory, permissions, tools, context management, and orchestration determine whether that intelligence becomes useful software.

## Lesson #3: context engineering becomes the human’s job

[Part 2 of Lauren’s guide](https://x.com/poteto/status/2097732320606507506) starts from an uncomfortable premise: frontier coding models can sometimes write individual pieces of code better than the human supervising them.

Humans still have to tell them what reality they are operating inside.

Lauren says she repeatedly sees two failures: the agent misunderstands intent, or it lacks the context required to do the work correctly. Both failures lead back to the quality of the context window.

Her solution is surprisingly indirect.

When someone reports a bug in Slack, she often asks the agent to read the conversation and **restate the problem in its own words before touching code**.

That does three jobs at once.

The agent compresses noisy human conversation into a problem statement. Lauren gets an early chance to catch a misunderstanding. And her own theory about the problem does not prematurely anchor the model on the wrong answer.

Then pstack can go hunting.

`/how` explores runtime mechanics. `/why` searches historical evidence across Git history, pull requests, Linear, Notion, Slack, Datadog, Sentry, code lineage, and analytics. `/teach` combines those findings into a model a human can understand. `/recall` pulls relevant context from earlier agent conversations.

The human’s role starts changing here.

You spend less time holding every line of the codebase in your head. You spend more time ensuring the agent has the right evidence to reconstruct the parts that matter.

That matches what Anthropic’s Claude Code team told us earlier this year. Their workflows increasingly revolve around [verification, agent routines, and keeping central context clean](https://www.theneuron.ai/explainer-articles/claude-code-creators-boris-cherny-and-cat-wu-explain-how-to-use-agent-loops/).

pstack makes that philosophy unusually explicit.

## Lesson #4: plan by touching reality

Lauren famously writes, **“I don’t believe in planning.”**

She does plan. She wants the plan to encounter reality as early as possible.

Traditional agent planning modes can create elaborate implementation documents before the model has attempted the hard parts. Lauren prefers working backward from a concrete artifact: an API tutorial, type signatures, a prototype, a screenshot, a benchmark, or running code.

For visual work, pstack’s prototyping playbook can build multiple throwaway variations, put them behind a switcher, drive each version using the application’s verification tooling, and capture screenshots or measurements for comparison.

Lauren’s line is useful: **“Prototyping is planning, but with code.”**

Architecture gets an even more elaborate loop.

`/architect` first researches the existing system. Then several independent agents can propose competing architectures, sometimes using different model families. A separate judge compares them. The winner becomes a type-and-interface sketch that implementation has to satisfy.

Reality gets veto power.

If implementation suddenly requires extra state, ugly casts, `any`, or repeated escape hatches across unrelated call sites, pstack treats those symptoms as evidence that the architecture itself may be wrong. The agent can scrap the design and restart.

That is a very different use of AI parallelism.

The goal is to buy more shots at the problem before an expensive decision hardens into the codebase.

## Lesson #5: parallelism comes after trust

Agent demos love the swarm.

Twenty agents! Fifty agents! Hundreds of agents!

Lauren’s sequence runs in the opposite direction.

First give one agent a reliable way to operate the product. Then give it enough context to understand the work. Then require evidence. **After that, parallelize.**

With a strong verification environment, she recommends cloud agents rather than loading a laptop with local Git worktrees. Each worker gets its own machine and can install dependencies, run the application, interact with it, and capture visual evidence.

`/swarm` can then send multiple agents through the same verification process, which opens interesting possibilities. A performance change can be tested across a larger sample. An application can be fuzzed for regressions. User reports arriving in Slack can automatically trigger reproduction attempts and eventually fixes.

The current pstack repo even includes a dormant **Benny automation pack** that triages Slack issue reports, reproduces confirmed bugs, fixes them, and collects real UI evidence.

Lauren says this approach helped her act as a “gardener” for Grok @Bot while the team was landing hundreds of pull requests per day. In Part 1 she says pstack enabled her to ship roughly **2,000 PRs per month with high confidence**, and Part 2 showed August ending at 2,462 PRs in production.

The raw number is less important than the operating model behind it.

When software creation gets extremely cheap, maintenance and verification become the scarce resources.

## Yes, this can be absurdly expensive

There is a strong argument against using pstack for everything: **sometimes the cure costs more than the disease.**

Rob O’Shaughnessy, aka Rob Shocks, put pstack through a practical test in a [13-minute walkthrough](https://www.youtube.com/watch?v=lUhXa8GiXns). He built the same skill-management project once without the stack and once with it.

His baseline run took about **30 minutes**.

The pstack run took about **one hour**.

Arena, Swarm, multi-model reviews, tests, verification, and audits all require more inference. Rob says plainly that the stack burns a lot of tokens.

He still preferred the hardened result.

The pstack run built verification scripts, cross-checked behavior, and eventually caught **three false claims the agent itself had hallucinated** during development.

His conclusion is probably the right one: you do not need to “throw the potato” at a tiny UI tweak. A critical feature, major refactor, production bug, architecture change, or autonomous overnight run creates a very different cost equation.

A useful mental model is:

**Spend more agent compute where being wrong is expensive.**

The plugin makes that trade unusually visible because its rigor has an actual token bill.

## The most useful part of pstack may be the parts you steal

You can install pstack directly in Cursor with `/add-plugin pstack`, then configure model routing through `/setup-pstack`. The plugin is open source under MIT, and its current marketplace listing is verified by Cursor.

You can also learn a lot from the repo without adopting Lauren’s exact setup.

The transferable ideas are simpler:

*   **Give agents tools instead of repeatedly explaining procedures.**
*   **Define success in terms of observable evidence.**
*   **Make the agent reproduce a bug before fixing it.**
*   **Measure performance before optimizing it.**
*   **Keep a compact, maintained map of the product.**
*   **Recover historical context before making architectural assumptions.**
*   **Ask the agent to explain the problem in its own words.**
*   **Prototype competing ideas before committing.**
*   **Use multiple models where independent judgment is valuable.**
*   **Keep the main context window clean by delegating bounded work.**
*   **Turn recurring lessons into skills, scripts, lints, or checks.**
*   **Reserve expensive multi-agent rigor for work that earns it.**

This is where pstack gets more interesting than Cursor.

The software industry spent the first wave of coding agents asking how much code a model could generate. pstack is built for the next problem: **how do you run an engineering organization when code generation stops being scarce?**

Lauren’s answer looks a lot like industrialization.

You build gauges. You make procedures reproducible. You keep operational memory. You separate workers. You inspect output. You record failures and improve the machinery that produced them.

The agent becomes replaceable. The system around it compounds.

## Where pstack goes from here

Some of this machinery may eventually disappear into the coding agents themselves.

Rob notes that stronger future models could naturally adopt more of these disciplines. Cursor, Anthropic, OpenAI, and others are already baking agent routing, subagents, planning, verification, memory, and long-running loops into their own harnesses.

That creates the most interesting unanswered question around pstack:

**How much engineering process should live inside the model, how much belongs in the agent harness, and how much should remain encoded by the individual team?**

Lauren’s current repo already hints at one answer. `/automate-me` can inspect how _you_ work and draft a personalized `-mode` skill while using pstack underneath. The base machinery stays shared; the judgment layer becomes yours.

That may be the durable idea here.

The winning agent setup probably will not be one gigantic prompt telling the AI how to behave. It will look like an accumulated operating system for how a person or team gets work done: its standards, tools, memory, verification loops, preferred models, debugging habits, and scar tissue from everything that failed before.

pstack is Lauren Tan’s version of that operating system.

Reading it is useful even if you never install the plugin.

### A note on Rob’s other links

Rob’s [OpenRouter sponsor shortlink](https://openrouter.plug.dev/8PkzKBOA) currently lands on Dub’s “Link Not Found” page.

His [Switch Dimension “Build With AI” course/community](https://www.switchdimension.com/) is currently waitlist-based and advertises more than seven hours of project-based material covering Claude Code, Cursor, Codex, and a Next.js/Tailwind/Supabase/Node stack. The page does not currently expose a public price.
