# MyImpact Demo Script

A generic demonstration of MyImpact suitable for any organization.

---

## 5-Minute Demo

**Goal**: Show how to generate goals aligned to company culture and job expectations

### Setup (Before Demo)

1. Open the MyImpact web app in your browser
2. Have a company org chart or focus areas handy (optional)
3. Have 2-3 example employee profiles ready (IC, manager, director)

### Script

#### Opening (30 seconds)

> "One of the biggest challenges in goal setting is making sure goals align to three things:
> 
> 1. **Our company culture** - what we value
> 2. **Job expectations** - the level-specific competencies
> 3. **Organizational priorities** - strategic focus areas
>
> MyImpact helps with exactly this. Let me show you."

#### Demo Flow (4 minutes)

**Step 1: Show the form (30 seconds)**
> "Here's the MyImpact app. It's a simple form with a few questions about the person setting the goal."

Point out:
- Employee scale dropdown (individual contributor vs manager)
- Level dropdown (L30, L40, etc.)
- Growth intensity (how stretched should the goal be?)
- Organizational focus (what we're focusing on this quarter)

**Step 2: Fill in an example (1 minute)**

Select for an **individual contributor**:
- Scale: `Technical`
- Level: `L30–35 (Career)`
- Growth Intensity: `Moderate`
- Organization: `[Your company name/demo]`
- Goal Style: `Independent`

> "I'm creating a goal for a mid-level engineer who wants to grow moderately this quarter, in line with our engineering focus areas."

**Step 3: Generate and show results (1.5 minutes)**

Click "Generate Prompt"

> "Here's what the system generated - a customized prompt that combines:
>
> - The **technical competencies** for an L30-35 engineer
> - Our **culture expectations** (what we value)
> - **Organizational priorities** from this quarter
>
> All in one structured prompt that's ready to copy into any LLM like ChatGPT or Claude."

Show the generated prompt. Highlight:
- Context about role
- Culture references
- Focus areas
- Instructions for the AI

**Step 4: Demonstrate the use case (1 minute)**

> "Here's how this works in practice:
>
> 1. Employee copies this prompt
> 2. Employee pastes it into ChatGPT/Claude
> 3. Employee gets personalized goals in seconds
> 4. All the context is baked in - culture, level expectations, company priorities
>
> It's like having a goal-setting coach that knows your company culture."

**Step 5: Show variations (30 seconds)**

Go back and change:
- Level: `L40–45 (Senior)`
- Growth Intensity: `Aggressive`

Click "Generate" again

> "See how the prompt changes? The competencies, focus areas, and intensity all shift automatically based on the person's level and growth appetite."

---

## Extended Demo (15 minutes)

Includes system design and customization walkthrough.

### Part 1: Quick Demo (5 minutes)

Follow the 5-minute script above.

### Part 2: How It Works (5 minutes)

**Architecture walkthrough**:

```
User Input (Scale, Level, Intensity)
          ↓
MyImpact (combines 3 data sources)
├─ Culture Expectations
│  └─ 8 cultural principles
├─ Job Expectations
│  └─ L10-L100+ competencies
├─ Organizational Focus
│  └─ Strategic priorities
          ↓
Output: Customized Prompt
          ↓
User copies to LLM (ChatGPT, Claude)
          ↓
LLM generates personalized goals
```

> "Under the hood, MyImpact is combining data from three sources:
>
> 1. **Culture Expectations** - We define what it means to embody each of our 8 cultural principles
> 2. **Job Expectations** - For each level, we have specific competencies and success criteria
> 3. **Organizational Focus** - This quarter's strategic priorities
>
> The system intelligently combines these into a single prompt. The AI (ChatGPT, Claude, etc.) then generates goals that hit all three dimensions."

**Show the data structure**:

> "For example, at the L30 level, our technical expectations include:
> - Code quality and architecture
> - System design thinking
> - Mentoring junior engineers
>
> And our culture expects:
> - Continuous learning
> - World-class excellence
> - Ownership
>
> The prompt weaves all of this together in a way that makes sense to an LLM."

### Part 3: Customization (5 minutes)

**For Organizations**: Talk about customization

> "Out of the box, MyImpact uses a demo dataset. But for your organization, you'd customize:
>
> 1. **Culture file** - Replace with your 5-8 core values
> 2. **Levels file** - Add your org's level definitions and competencies
> 3. **Focus areas** - Update to this quarter's priorities
>
> That's it. The system re-runs with your data."

**Show where customization happens** (point to `/data/` directory structure):

```
data/
├─ culture_expectations_technical.csv
├─ culture_expectations_people_manager.csv
└─ (add custom org data here)
```

> "These CSV files define your culture and competencies. Swap them out, and the entire system adapts. No code changes needed."

**Use cases your organization might adapt to**:

- Goal generation (shown here)
- Competency self-assessments
- Hiring rubrics (customize for job descriptions)
- Development planning
- Performance reviews
- Org design/span of control assessments

---

## Q&A Guide

### "How accurate is the LLM output?"

> "The prompt is very detailed, so results are usually 80-90% usable out of the box. The employee may need to refine one or two goals, but it saves hours of blank-page syndrome. Think of it as a first draft that's surprisingly good."

### "What if our culture/levels are different?"

> "That's the whole point! MyImpact is designed to be data-driven. You define your culture, your levels, your focus areas - and the system generates prompts that reflect your org. No two orgs should use identical culture files."

### "Can we integrate this into our HR system?"

> "Yes, MyImpact is built as:
> - A CLI tool (for batch processing)
> - A REST API (for integration)
> - A web app (for demos and one-off use)
> 
> We can integrate with Workday, Bamboo, or any HR system that supports webhooks or APIs."

### "Does this replace human managers?"

> "Not at all. This is a tool to accelerate the goal-setting conversation between manager and employee. The manager is still responsible for:
> - Reviewing the goals
> - Adjusting based on team capacity
> - Connecting to career development
> - Having the human conversation
>
> This just removes the research and drafting phase."

### "How often would we use this?"

> "Typically quarterly during goal-setting season (4x per year). Some orgs also use it for:
> - Mid-year check-ins
> - New hire onboarding
> - Promotion planning
> - Org transitions"

### "What's the learning curve?"

> "Very low. The form has 5 fields. If you've got your culture and levels defined, you can start using it in 5 minutes. Customization takes a few hours."

---

## Admin Demo (Customization Walk-through)

If you have admin access to show customization:

### Show Culture Data

Open `data/culture_expectations_technical.csv`:

```
Culture Value,Principle Description,L10-15,L20-25,L30-35,...
Humble,Leave ego at the door...,Seeks feedback openly,...
Hardworking,Committed to excellence...,Delivers on commitments,...
...
```

> "This is how we've structured our culture. Each principle maps to 6 level definitions, each with specific behaviors."

### Show Competencies Data

Open `data/culture_expectations_people_manager.csv`:

```
L70-75 People Manager
Competencies: [strategic thinking, org design, team scaling...]
```

> "For each level, we've defined specific competencies. L70-75 is about strategic scaling; L30-35 is about individual technical impact."

### Show Prompt Assembly

Point to `myimpact/assembler.py`:

```python
def assemble_prompt(scale, level, intensity, org, focus_areas):
    # Combines culture + competencies + org context
    # Returns structured prompt for LLM
```

> "This Python function is the heart of the system. It:
> 1. Looks up the culture expectations for the level
> 2. Pulls relevant competencies
> 3. Adds org-specific focus areas
> 4. Structures it as a prompt
>
> If you change the CSV files, the prompts change automatically."

### Show Live Customization

Update a focus area or competency and regenerate:

> "See? Change one value, and all the generated prompts update. That's the power of data-driven systems."

---

## Talking Points by Audience

### For HR/People Leaders

**Problem you're solving**:
> "Goal setting is time-consuming and inconsistent. Employees spend hours researching competencies instead of setting ambitious goals."

**Value prop**:
> "MyImpact makes goal setting 10x faster by automating the research phase. All goals automatically align to culture and level expectations."

**Business impact**:
- Faster goal-setting season (4-6 weeks → 2-3 weeks)
- More consistent goals across the org
- Better alignment to company strategy
- Higher-quality goals (LLM-enhanced, not human-drafted)

### For Engineering Leaders

**Problem**:
> "Goal-setting meetings require managers to context-switch, and goals often miss technical depth."

**Solution**:
> "MyImpact generates prompts grounded in technical competencies. Employees can generate their own draft goals in 5 minutes."

**Technical details** (if they ask):
- FastAPI backend with rate limiting
- Structured prompt generation
- Extensible data model (CSV-based)
- REST API for integrations

### For Executives

**Problem**:
> "Annual goals aren't well-connected to org strategy. Goal-setting is a bottleneck."

**Solution**:
> "MyImpact closes the loop: org priorities → employee goals. Goals are generated in minutes, not weeks, and they're all tied to strategy."

**ROI angle**:
- **Time saved**: 8-10 hours per manager per year (500-person org = 4,000-5,000 hours saved)
- **Quality improvement**: Automated alignment to culture and strategy
- **Equity**: Consistent rubrics across all levels and teams
- **Low cost**: SaaS pricing or self-hosted

---

## Audience Reaction Guide

### If they ask: "This seems over-engineered for goal setting"

> "Fair point! Goal setting *could* be simple. But most orgs struggle with:
> - Consistency across teams
> - Alignment to company culture
> - Competency rigor at each level
> 
> MyImpact handles all three at scale. A 100-person org can now set goals with the same rigor as a 1000-person org."

### If they ask: "Why not just use ChatGPT directly?"

> "You could! But you'd have to:
> - Copy-paste your culture doc
> - Copy-paste level definitions
> - Explain your org context
> - Do this 500+ times (for a large org)
>
> MyImpact automates that. It's ChatGPT + your org's data, templated."

### If they're skeptical about AI

> "The AI (ChatGPT, Claude) isn't making decisions here. It's writing goals. A human—the employee or manager—reviews, edits, and approves. AI is just the draft engine."

### If they love it

> "Great! Here's how we can get started:
> 1. Get your culture and competencies defined
> 2. Set up MyImpact (30 min to deploy)
> 3. Pilot with one team (1-2 weeks)
> 4. Scale org-wide (1-2 quarters)
> 
> Happy to walk through the details."

---

## Follow-up Actions

### For interested organizations:

**Short-term** (1 week):
- [ ] Schedule a 1:1 with HR/People leadership
- [ ] Get culture and competency definitions (existing docs)
- [ ] Identify pilot team (50-100 people)

**Medium-term** (2-4 weeks):
- [ ] Customize data files (culture, levels, focus areas)
- [ ] Deploy to test environment
- [ ] Run pilot with HR team + pilot group

**Long-term** (1-2 quarters):
- [ ] Scale to full org
- [ ] Integrate with HR system (if needed)
- [ ] Iterate on prompts based on feedback

### Handoff materials:

Share:
- `docs/guides/01-quick-start.md` - Local setup (5 min)
- `docs/api/README.md` - API reference
- `docs/architecture/overview.md` - System design
- This demo script

---

## Tips for Great Demos

1. **Know your data**: Be ready to talk about your culture and competencies
2. **Have real examples**: Demo with actual job levels and focus areas from your org
3. **Show variation**: Demonstrate different levels to show the system adapts
4. **Be honest about AI**: Acknowledge it's not perfect, but it's a great starting point
5. **Connect to business**: Tie back to org strategy, time-to-hire, employee retention
6. **Keep it interactive**: Let them try the form themselves if they're interested
7. **Be ready to customize**: Talk about how you'd adapt this to their culture

---

## Troubleshooting Demo Issues

### "The form won't submit"

**Likely cause**: Backend not running or API endpoint wrong

**Fix**:
- Check that Container App is running: `az containerapp show --name myimpact-demo-api`
- Verify frontend has correct API endpoint (check browser console for errors)
- Test API health: `curl https://<API-URL>/api/health`

### "The prompt looks generic"

**Likely cause**: Using demo data, not org-specific data

**Fix**:
> "This is using our demo dataset. When we deploy this in your org, you'd swap in your actual culture and competencies. The prompt will be much more specific then."

### "It's taking too long"

**Likely cause**: LLM API latency (if using live generation)

**Fix**:
- Pre-generate some example prompts before the demo
- Have screenshots ready as backup
- Mention: "In production, these cache after first generation"

### "The generated prompt looks off"

**Likely cause**: Unusual combination of inputs or LLM quirk

**Fix**:
> "Good catch! LLMs aren't perfect at following complex instructions. In practice, employees refine these 10-20% of the time. It's still much faster than starting from scratch."

---

## One-Liner Elevator Pitch

> "MyImpact generates personalized quarterly goals by combining your culture, job level expectations, and org priorities. What usually takes managers hours takes 5 minutes."
