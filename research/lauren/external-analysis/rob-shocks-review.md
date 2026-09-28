Title: Pstack Is Agent Overkill. Use It Anyway!

URL Source: https://moderncreator.app/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway

Published Time: 2026-09-08T00:00:00Z

Markdown Content:
Big Idea
## The argument in one line.

Pstack turns one senior engineer's personal discipline into a router plus a library of skills any coding agent can call, trading roughly double the build time for a much more verified, hardened result.

Who This Is For
## Read if. Skip if.

READ IF YOU ARE…

*   You already build on an established codebase with Claude Code, Cursor, or Codex and want a pre-built set of engineering discipline instead of writing your own skills from scratch.
*   You're managing several different agents or skill sets and want ideas for how to organize, route, and verify them.
*   You care about verification of non-deterministic agent output and want scripted, repeatable checks instead of trusting a green test run.

SKIP IF…

*   You're starting a brand-new project with no code yet. Pstack has no planning skill on purpose; it assumes the codebase already exists.
*   You're doing small front-end tweaks or minor UI changes where the token and time cost of multi-model verification isn't worth it.

TL;DR
## The full version, fast.

Pstack is Lauren Tan's personal skill stack for coding agents, built from 21 principles, 22 playbooks, and 24 skills, and it deliberately skips planning because its author believes the code itself is the best spec. Rob runs it live to build a skill manager: Potato Mode routes each prompt to the right playbook, Arena pits multiple models against the same design and grafts the best parts together, Swarm parallelizes different slices of one task, and skills like Why, Recall, and Interrogate pull real context and cross-examine finished code. The core discipline is verification: passing tests isn't proof anything works, so pstack scripts checks against the real running app and audits its own transcript for false claims. The tradeoff is cost. The same build took about twice as long with the full stack attached as it did with no plan mode and no skills at all.

Free for members

## Chat with this breakdown — free.

Sign in and you get 23 free chat messages on us — ask for the hook, quote a framework, find the exact transcript moment, generate a markdown action plan. Bring your own key when you want unlimited.

[Create a free account →](https://moderncreator.app/)

Atomic Insights
## Lines worth screenshotting.

*   A single engineer's personal skill stack was reportedly run 10,000 times in one week by her own company's engineering team before she open-sourced it.
*   Pstack has no planning skill by design, because its author's stated position is that the best spec is the code itself.
*   The Arena skill runs the same design problem past three or four different models, then grafts the best parts of each into one final commit.
*   Swarm differs from Arena by splitting one task into different slices for parallel workers, then aggregating their separate results into a single report.
*   The Why skill checks tools like Slack, Sentry, and product analytics, not just the codebase, to reconstruct the real reason a past decision was made.
*   The Laziness Protocol biases an agent toward deleting code and taking the smallest change that solves the problem, on the logic that smaller changes stay maintainable.
*   Redesigning from first principles means asking how the code would be structured if the new feature had been a day-one requirement instead of a bolt-on.
*   The stated goal of the whole stack is maximum impact with the least amount of code, not writing more code.
*   The Unslop skill exists specifically to strip AI writing tells like 'delve,' 'crucial,' and em dashes out of anything an agent writes.
*   A passing test suite and a clean compile are treated as insufficient proof a feature works, so verification skills script checks against the real running artifact.
*   A self-audit against the session transcript caught the agent having made three false claims about what it had actually done.
*   Running the same build with the full stack attached took about an hour versus roughly thirty minutes with no plan mode and no skills at all, close to double the time for a more hardened result.

Takeaway
## A senior engineer's rulebook for running coding agents

AGENT ENGINEERING

Pstack packages one engineer's verification-first discipline into skills any agent can run, and it costs roughly double the time for a measurably more hardened build.

01 Pstack Intro and Setup

*   Pstack is one engineer's personal skill stack for coding agents, structured as 21 engineering principles, 22 playbooks, and 24 skills.
*   It ships officially for Cursor and has an unofficial port to Claude Code, Codex, and OpenCode maintained separately.
*   It's built to run on an already-established codebase, not to help plan a new one from scratch.

02 PStack Skills

*   Potato Mode is the router: it reads the prompt and decides which of the 20+ skills should run first.
*   Arena pits three or four different models against the same design problem, then grafts the best parts of each into one final commit.
*   Swarm splits a task into different slices of the same problem for parallel workers, then aggregates the results into one report.
*   The Why skill checks tools like Slack, Sentry, and product analytics, not just the codebase, to reconstruct the real reasoning behind a past decision.

04 Rob's Favourite Skills

*   Recall rebuilds your working context from stored transcripts when picking a project back up after time away.
*   Interrogate has two or three different models cross-examine the same finished code against its own standards before it ships.
*   Unslop strips AI writing tells like delve, crucial, and em dashes out of anything an agent writes.
*   Bro restates a dense technical update in plain language when too many agents running at once make it hard to follow.

05 PStack Methodology

*   A build starts with a cheap probe: a small script that tests whether the idea is even possible before any real app gets built.
*   Plans made before the agent touches real code get broken once building actually starts, forcing a rework mid-build.
*   A self-audit against the session transcript caught the agent having made three false claims about what it had actually done.

06 Lead Principles of Agent Engineering

*   The Laziness Protocol biases toward deleting code and taking the smallest change that solves the problem, because smaller changes stay maintainable.
*   Redesigning from first principles means asking how you'd structure the code if the new feature had been a day-one requirement instead of a bolt-on.
*   The stated goal isn't writing more code, it's maximum impact with the least amount of code, which sometimes means removing existing structure.
*   Passing tests and a clean compile aren't proof a feature works; real verification means checking the actual running artifact.

07 PStack vs No Stack

*   The same project took about twice as long with the full stack attached, roughly one hour versus thirty minutes with no plan mode and no skills.
*   The extra time bought a more hardened, more verified application, not just a faster one.
*   For small design tweaks or front-end UI work, the reviewer's own take is that the full stack usually isn't worth the overhead.

Glossary
## Terms worth knowing.

Potato Mode Pstack's router skill. It reads the incoming prompt and decides which of the 20-plus other skills should handle it first.

Arena A skill that runs the same design problem through three or four different models in parallel, then grafts the strongest parts of each result into one final commit.

Swarm A skill that splits one task into separate slices of the same problem for parallel workers, then aggregates all their work into a single combined report.

MCP Model Context Protocol. A standard way for an agent to connect to outside tools and data sources, such as Slack, Sentry, or a product analytics platform.

TDD (Test-Driven Development)Writing the failing test for a bug or feature first, then writing the code that makes it pass.

Diarization Automatically labeling who is speaking at each moment in an audio transcript. Not part of pstack itself, referenced here as background context for the video pipeline.

ADR (Architectural Decision Record)A short written record of why a particular technical decision was made, so the reasoning survives after the people involved move on.

Resources
## Things they pointed at.

01:22 tool Michael Denyer's Claude Code / Codex / OpenCode port of pstack

Quotables
## Lines you could clip.

02:23

> “"The Best Spec Is The Code"”

single-line thesis for the whole no-planning stance→ TikTok hook[↗ Tweet quote](https://x.com/intent/tweet?text=%22%22The%20Best%20Spec%20Is%20The%20Code%22%22%20%E2%80%94%20Rob%20Shocks%20via%20%40moderncreatorhq&url=https%3A%2F%2Fmoderncreator.app%2F2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway)

03:15

> “"pstack gives you fearless parallelism"”

punchy claim, sets up the Arena/Swarm segment→ IG reel cold open[↗ Tweet quote](https://x.com/intent/tweet?text=%22%22pstack%20gives%20you%20fearless%20parallelism%22%22%20%E2%80%94%20Rob%20Shocks%20via%20%40moderncreatorhq&url=https%3A%2F%2Fmoderncreator.app%2F2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway)

07:08

> “"cleaning up writing, removes AI tells"”

on-screen definition of the Unslop skill, plain and quotable→ newsletter pull-quote[↗ Tweet quote](https://x.com/intent/tweet?text=%22%22cleaning%20up%20writing%2C%20removes%20AI%20tells%22%22%20%E2%80%94%20Rob%20Shocks%20via%20%40moderncreatorhq&url=https%3A%2F%2Fmoderncreator.app%2F2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway)

09:59

> “"The goal isn't more code. It's maximum impact with the least amount of code."”

stated thesis of the whole principles section→ TikTok hook[↗ Tweet quote](https://x.com/intent/tweet?text=%22%22The%20goal%20isn%27t%20more%20code.%20It%27s%20maximum%20impact%20with%20the%20least%20amount%20of%20code.%22%22%20%E2%80%94%20Rob%20Shocks%20via%20%40moderncreatorhq&url=https%3A%2F%2Fmoderncreator.app%2F2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway)

12:05

> “Using Fable 5.1 without any plan mode and without any skills attached it took about 30 minutes to get the project done. Using the P-Stack it took one hour.”

the honest cost-benefit number the whole video is arguing about→ newsletter pull-quote[↗ Tweet quote](https://x.com/intent/tweet?text=%22Using%20Fable%205.1%20without%20any%20plan%20mode%20and%20without%20any%20skills%20attached%20it%20took%20about%2030%20minutes%20to%20get%20the%20project%20done.%20Using%20the%20P-Stack%20it%20took%20one%20hour.%22%20%E2%80%94%20Rob%20Shocks%20via%20%40moderncreatorhq&url=https%3A%2F%2Fmoderncreator.app%2F2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway)

The Script
## Word for word.

Read-along

### Don't just watch it. Burn it in.

See every word as it's spoken — crank it to 2× and still catch all of it. The same dual-channel trick behind Amazon's Kindle+Audible.

17 px

metaphor analogy story

So this is Lauren Tan, Ninja Engineer. She's worked at Netflix. She's a member of the core React team.

You might have heard of React. And principal engineer at SpaceX and also Cursor. If you're building coding agents or using any kind of software factory, you have to check out her set of skills.

It's basically a senior engineer's brain extracted into one stack. Even our friend Theo has done a deep dive on how awesome her skills are. So even if you don't end up using P -Stack, just reading them will give you a breakdown of how a serious agent practitioner works at scale.

So in just one afternoon, I created this skill manager called Motenbase to manage all my skills across my various different agents. I'll take you through some of that process and a breakdown of all the noteworthy skills. This is a couple of minutes that's really going to help you improve your work with agents.

P -Stack is broken down into all of her principles and engineering rules. Then we've got the playbooks, which you can think of as operating procedures so the agent knows what to do next. And then all the individual skills and slash commands that do all the work.

Even after using Agents for two years and building my own set of skills, there are a few in here that are absolutely getting added to my default list. So you can run Pstack anywhere you want. Cursor, Cloud, Code, Codex.

You can find the official repo from Cursor and Lauren at plugins .pstack .cursor. I'll leave the link in the description down below. And it's as simple as just typing in slash add plugin P stack when you're in cursor.

If you want to run this on cloud code codex open code, I found this not official repo by Michael Denyer. He's done the porting into each one of the agents. So you can actually run that by installing it from the plugin marketplaces.

So the heart of the P stack is potato mode. It's essentially a router that helps you decide which one of the 20 plus skills you should use first. So what we've got here in our skill tree is essentially 22 playbooks, which gives a nice set of examples here for different use cases along with each one of the prompts.

I always love an opportunity to build some new software. I haven't found a good skill manager that I like using, so let's go and build our own. So I've given potato mode a prompt here and let's see which one of its skills it uses to kick this off.

So the first thing we see here is potato mode actually rooted this to a figure it out playbook. If you're expecting something like BMAD superpowers or open spec, this isn't necessarily designed for spec and planning. This is meant to be operated on an established code base.

Lauren's personal take on this is I don't believe in planning. The best spec is the code. So there's deliberately no planning skill baked into P stack.

Now you can already see the arena skill is in place. So we have a design idea distributed between Claude, GPT, Grok and Claude Opus 5. There goes the token budget.

If you have a critical feature to develop and tokens are not an issue you can run arena. It pits three or four different agents against the same problem and it takes the best parts of each and wraps them into a final commit. And it's something that Cursor had baked in six months ago and they later removed.

So basically having them all fight it out to give the best design and then picking the best parts of each design. So based on what each one of the sub -agents learned while working on the problem, Arena decides to either graft or reject. Now, similar to that, we have the idea of swarm.

It's the idea that, again, you've got parallel workers, but you give them different slices of the problem. And then you pull it all back into one aggregated report. PStack is designed so you get fearless parallelism.

If you're working across feature branches, work trees, etc. Even if you're using Arena or Swarm, it's aggregating all of your work together, making sure there's no overlaps. Well, that's the idea in principle.

It is a big claim. I haven't used it enough to say that that is actually the case, but you can see how the principles are baked in to allow for it. Using its TDD skill or Test Driven Development, it went and created a bunch of unit tests first and then made sure they passed before proceeding.

So this skill I particularly like, Y. So the Y skill is really cool. Instead of just checking the transcript for the project, it basically runs through all the different MCPs and CLIs that you have that are relevant to the project.

It might check product information in post -hoc. It might go to a conversation thread in Slack about why a feature was implemented. It might pull logs from Sentry to get a full big picture of decision records or ADRs as to why something was done.

Definitely stealing this one. So just like Potato Mode is a router for all the skills in P -Stack, OpenRouter is pretty much a router for all the models you could possibly want to use. Basically, one API key and one bill gets you all the text, video, voice, and image models you could possibly want under one API endpoint.

There are so many reasons why that is awesome, but for today, here's just one. I get so tired of logging into different dashboards, figuring out what API keys I have, switching around providers for video and images, and not to mention my poor agent has to manage so many different APIs. So I went and built a CLI that interacts with Open Router's API.

I want to be able to generate images, videos, and voice using any provider, using Cloud Code, Cursor, or Codex, and create a singular skill that can invoke the CLI. So basically, I got my agent to build a CLI that connects to Open Router along with a set of skills so I can generate images, videos, text and even audio.

I just need to grab one API key. So then I can use my new skill in CLI via Open Router's API to do things like generate a video of a load of potatoes rotating around my head using Seedream. And just like that, we have a head full of potatoes.

Rob Shocks viewers can check out Open Router via the link in the description down below. Next up in terms of usefulness, we have Recall. So Recall is fantastic for when you want to pick up on a project that you've just left off.

Maybe it's been a week or so. You're trying to remember where you're at. It will scan through all the transcripts.

It'll even use the why skill to go and check your MCPs like Notion, Linear or PostHog to find out where we're at and what we need to do next. To be honest, just reading through the skills themselves, there's some great learning in here for developers. Some fantastic patterns that are really worth knowing.

So once the code is actually developed, we're into the validation stage. So we have interrogate. So with interrogate, you're basically getting two or three different models to go and interrogate or double check the code against its standards.

Multiple different models review the same code and they all come back with their opinions. Now you're going to burn a ton of tokens with some of these skills, but inevitably if what you're looking for is the highest and strictest code quality, the token count probably isn't going to matter to you here. This one I absolutely love.

It's the create verification skill. So basically it created its own scripted way to prove out the app behavior. We have to delve into the route, multiple different projects and setups.

We have to scan continuously to make sure that everything's updated. There is a large surface area for this app to appear to be working, but actually be fundamentally broken or giving us the wrong data. So it went and created a set of verification scripts and cross checks.

When you're dealing with non -deterministic agents, this kind of verification step is just so valuable. We also have a maintain verification skill. So oftentimes as the app develops, the script or verifier that you've set up is going to diverge from the development.

So running this skill will actually go back and make sure that it gets updated. The unslap skill is an absolute gift if you use your agents to do any form of writing. With the purpose of killing and removing all those annoying phrases like pivotal moment, crucial, delve, enduring.

And the controversial one. getting rid of EM dashes entirely. I actually like EM dashes.

I used them a long time before AI came along. Sad to see them go, but inevitably it seems like a big tell for people that AI is used when you see that little line. Let's say I've been running a load of agents in parallel all morning and my brain is just coming to a halt.

This is just too much for me to grok. I can actually run the bro skill, which basically restates the last message in plain human language with no jargon. So let's give it a go.

This bro skill is an absolute gift for clarity, particularly when your brain has been burning hard on 10 different agents.

So we can learn an awful lot about P -Stack, how it works from the show me your work skill. So I ran this on the first invocation of that one prompt. Now remember this whole thing was one shot of that one single prompt we started with.

So just like any good engineer, it started with some probing. So a probe can be a quick test to see if what we're trying to achieve is even possible. We're not going to build a whole app.

We're just going to write a small script and just investigate to see if it is actually possible. So the initial frame is understanding the requirements and the constraints of the ask. So in this case, we're saying that we wanted to operate on Mac, but then eventually on other systems.

So it's able to create a frame around what needs to be built. Next up, we did some basic scaffolding for the app before we moved into the arena stage. where we had four parallel agents working on the problem.

So this one is particularly interesting. Design changes forced by reality. now this can sometimes be the problem with doing too much planning up front when the agent creates this very detailed plan it hasn't actually dealt with reality yet it's only as we build and develop that our assumptions get broken and we have to rework the problem and come up with a new plan on the fly in phase e here we have all the verification testing and then we finish up with our audit Now, this is why verification is so important.

The agent had realized it had hallucinated some of the details. It called three false claims that it was able to correct.

So let's take a look at the key principles. Number one, laziness protocol. Absolutely love this one.

When refactoring our code, let's look to delete code if possible and make this a whole lot simpler rather than adding more code. And let's just aim for the smallest change to get the job done because inevitably that leads to far more maintainable code later on. So redesigning from first principles.

So as your project grows and you're adding more features, the agent might decide to bolt on the next feature or functionality. What redesigning from first principle is doing is basically saying that let's imagine that we're adding this feature from day one. How would you look at the code structure?

How would you have designed the scaffolding, the database, the structures in order to make sure this was more of a native feature? So this might actually involve removing some structures and some code in order to get to our happy place. So again from Lauren, the goal isn't more code, it's maximum impact with the least amount of code.

Minimizing reader load. We're all getting so sick of these huge PRs written by agents with disjointed code across several abstractions and modules. The idea here is that we minimize the reader load.

We keep things super simple with the minimum amount of abstractions. Exhaust the design space. So this is very much where the agent arena comes in.

We can have multiple different models and agents working on the same problem, come up with the best of all and then graft the best parts into our final commit. In my course, I teach this thing called design mode where we actually just scaffold out a couple of different variations of what the interface might look like without any database or code in the background so we can come up with the best option for a design before we move forward.

Next principle is build a lever. So if you're going to be doing something with your agent by hand multiple times, why don't you build a tool for that? It could be a CLI.

It could be a script that does the same verification over and over and again, which we see via the verification skill. Lauren has also baked in some great disciplines here. To be honest, you would hope that a model like Fable or Astra would start to think about and bake these things in naturally.

But when it comes to verification steps, there is no harm in having these kind of disciplines applied. after the fact. One of the biggest principles that flows through the entire stack is verification.

Having it compile and go green on tests is not the same as actually testing and proving it works in terms of a real artifact by deeper verification, whether that's via computer use or end -to -end testing. Guard the context window and never block the human. You can see this throughout the skills and the playbooks.

The central context window is key, it's important. How do we offload slices of the task to sub -agents? They've got their own unique context windows to do their work and then they report back to the central thread.

The combined skills and methodology, while costing a lot more in terms of time and tokens, have led to a much more hardened application. Using Fable 5 .1, Without any plan mode and without any skills attached it took about 30 minutes to get the project done.

Using the P -Stack it took one hour so twice the amount of time. However the difference between the two projects is substantial. Now let's be very clear P -Stack as a set of machinery and skills in your repo is going to cost you a lot more money.

All of this validation verification and swarms means a lot of token burning you might not need to throw the potato at every single project that you have but at least you have an idea of what it's good at and where it can be used if you're making small design changes or working on the front -end ui you probably don't need to be using this so if you're subscribed and i hope you are i've been building on a series of videos around skills and the sdlc for a modern agentic developer i've got a course coming up on that soon so if you want to get into the waitlist for the first cohort you can drop your interest at switchdimension .com

The Hook

## The bait, then the rug-pull.

A React core team engineer's personal skill stack was reportedly run 10,000 times in a week by her own company before she open-sourced it. This breakdown pulls apart what's actually in it, and whether it's worth the extra hour it costs to run.

Frameworks
## Named ideas worth stealing.

01:33 concept

### Potato Mode

The router skill that reads the incoming prompt and decides which of the 20+ other skills or playbooks should run first.

Steal for any setup juggling more than a handful of agent skills

02:27 concept

### Arena

Runs the same design problem through three or four different models, then grafts the strongest parts of each into one final commit.

Steal for a critical feature where token cost isn't the constraint

03:00 concept

### Swarm

Splits one task into different slices worked in parallel, then aggregates the separate results into one report.

Steal for large tasks that decompose cleanly into independent chunks

03:51 concept

### Why

Instead of only reading the codebase, checks connected MCPs and CLIs (Slack threads, Sentry logs, product analytics) to reconstruct the real reasoning behind a past decision.

Steal for onboarding onto an unfamiliar codebase or resolving a stale decision

05:22 concept

### Recall

Rebuilds working context from stored session transcripts and connected MCPs when picking a project back up after time away.

Steal for any project you step away from for more than a few days

05:47 concept

### Interrogate

Has two or three different models cross-examine the same finished code against its own standards before it ships.

Steal for code that needs the strictest possible quality bar, token cost aside

07:02 concept

### Unslop

Strips AI writing tells (delve, crucial, pivotal, em dashes) out of anything an agent writes.

Steal for any agent-generated copy, docs, or commit messages

09:21 concept

### Laziness Protocol

Biases an agent toward deleting code and taking the smallest change that solves the problem, because small changes stay maintainable.

Steal for any refactor prompt

09:37 concept

### Redesign from First Principles

Asks how the code would be structured if the new feature had been a day-one requirement, instead of just bolting it onto what exists.

Steal for a feature that's been patched onto the same structure repeatedly

10:36 concept

### Exhaust the Design Space

Builds two or three competing prototypes and compares them side by side before committing to one.

Steal for any non-trivial design decision with real alternatives

10:55 concept

### Build the Lever

If you're doing something by hand more than once, build a tool (CLI, script, or verification check) that does it instead.

Steal for any repeated manual verification step

11:44 concept

### Guard the Context Window

Offloads slices of a task to sub-agents with their own context windows, which report back to a lean central thread instead of bloating it.

Steal for long multi-step agent sessions that start losing coherence

CTA Breakdown
## How they asked for the click.

VERBAL ASK

12:21 newsletter

> “Build With AI, course and community waitlist”

Soft close, woven into a wrap-up thought rather than a hard sell; screen shows the landing page with an email capture form while he talks about the upcoming cohort.

MENTIONED ON CAMERA

FROM THE DESCRIPTION

Storyboard
## Visual structure at a glance.

[![Image 1: open](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0001.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0001.jpg)

hook open 00:00

[![Image 2: skill tree overview](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0010.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0010.jpg)

value skill tree overview 01:33

[![Image 3: sponsor: OpenRouter](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0026.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0026.jpg)

cta sponsor: OpenRouter 04:10

[![Image 4: favourite skills](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0033.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0033.jpg)

value favourite skills 05:20

[![Image 5: methodology walkthrough](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0048.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0048.jpg)

value methodology walkthrough 07:49

[![Image 6: engineering principles](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0057.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0057.jpg)

value engineering principles 09:12

[![Image 7: stack vs no stack](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0074.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0074.jpg)

value stack vs no stack 11:53

[![Image 8: course waitlist CTA](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0079.jpg)](https://modcreator-cdn.b-cdn.net/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway/frames/frame_0079.jpg)

cta course waitlist CTA 12:21
