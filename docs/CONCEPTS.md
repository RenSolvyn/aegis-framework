# Research Concepts — Plain English

You don't need a degree to understand these. Each concept is
explained the way you'd explain it to a friend over coffee.


## The basics

### Hypothesis
A guess you can test. Not just "I think X is true" but "I think
X is true, and here's how I'd check." If you can't check it,
it's an opinion, not a hypothesis.

Example: "I think watering tomatoes twice a day makes them grow
faster than watering once a day." You can test this. "I think
tomatoes are the best vegetable" — you can't.

### Variable
Anything that can change or differ. In "does watering frequency
affect tomato growth?" there are two variables: how often you
water (the thing you control) and how much they grow (the thing
you measure).

The one you control is called the **independent variable**.
The one you measure is called the **dependent variable**.

### Control group
The group you don't change. If you're testing whether a new
fertilizer works, the control group gets no fertilizer. Without
a control, you can't tell if your fertilizer did anything — maybe
all the plants would have grown that much anyway.

### Sample size
How many things you measure. Testing your fertilizer on 3 plants
tells you almost nothing — maybe those 3 were lucky. Testing on
300 tells you something real. Bigger samples = more reliable results.

The `power_check()` function in Aegis tells you how many you need.

### Replication
Can someone else do exactly what you did and get the same result?
If yes, your finding is probably real. If no, it might have been
a fluke, a mistake, or something specific to your setup.

This is why Aegis tracks everything — so anyone can retrace your
steps and try again.


## Understanding results

### Correlation
When two things tend to move together. "People who exercise more
tend to weigh less" is a correlation. It does NOT mean exercise
causes weight loss — maybe healthier people choose to exercise.

Correlation is measured from -1 to +1:
- 0.0 = no relationship at all
- 0.3 = weak relationship (probably real but small)
- 0.5 = moderate relationship (worth paying attention to)
- 0.7 = strong relationship (hard to ignore)
- 1.0 = perfect relationship (almost never happens in real data)

Negative values mean the opposite: as one goes up, the other
goes down.

### Causation
When one thing actually makes another happen. "Dropping a glass
causes it to break" — that's causation. Much harder to prove
than correlation. Most research finds correlations and then
designs specific experiments to test causation.

A correlation between ice cream sales and drowning deaths doesn't
mean ice cream causes drowning. Both increase in summer.

### P-value
The probability of seeing your result if nothing is actually
happening. A p-value of 0.03 means: "If there's really no
effect, there's only a 3% chance I'd see data this extreme."

Common threshold: p < 0.05 (less than 5% chance of a fluke).

What p-values do NOT mean:
- NOT "there's a 95% chance I'm right"
- NOT "the effect is large or important"
- Just "this probably isn't random noise"

### Effect size
How big the difference is. A drug might have a p-value of 0.001
(very unlikely to be a fluke) but only reduce symptoms by 2%.
That's a real effect, but it's tiny. Effect size tells you
whether a real result is also a meaningful result.

Common measure (Cohen's d):
- 0.2 = small effect (real but you'd barely notice)
- 0.5 = medium effect (noticeable)
- 0.8 = large effect (obvious)

### Statistical significance
When a result is unlikely to be a fluke (usually p < 0.05).
This is a minimum bar, not a gold standard. A result can be
statistically significant but practically meaningless (tiny
effect size), or practically important but not statistically
significant (too few samples).

Always report both the p-value AND the effect size. A result
with p = 0.04 and d = 0.1 is "real but tiny." A result with
p = 0.06 and d = 0.9 is "not quite proven but potentially huge."

### Confidence interval
A range of plausible values. Instead of "the average is 42,"
a confidence interval says "the average is between 38 and 46,
and I'm 95% confident the true value is in that range."

Wider interval = less certain. Narrower = more certain.
More data = narrower intervals.


## Avoiding mistakes

### Confound
Something you didn't control for that might explain your result.
You test whether music helps students study. The music group
studies in the morning; the no-music group studies at night.
Time of day is a confound — maybe morning studying is better,
not the music.

The `devils_advocate()` function asks you to identify confounds
before you publish.

### Bias
When something systematically pushes results in one direction.
If you only survey people who visit your website, you're missing
everyone who doesn't have internet. Your results are biased
toward internet users.

Aegis's 3-role pipeline exists specifically to prevent
confirmation bias — the tendency to see what you want to see
in your own data.

### Cherry-picking
Reporting only the results that support your hypothesis and
hiding the ones that don't. If you run 20 experiments and
one shows p < 0.05, that one is probably a fluke — by random
chance, 1 in 20 experiments will show "significance."

Pre-registration prevents cherry-picking: you state your
prediction before you see the data, so you can't pretend you
predicted whatever happened.

### Multiple comparisons
If you test 100 things, about 5 will appear significant by
chance (at p < 0.05). If you run many tests, you need to
adjust your threshold. Common methods: Bonferroni correction
(divide p by number of tests) or false discovery rate control.

### Overfitting
When your model memorizes the specific data instead of learning
the underlying pattern. A model that perfectly predicts last
year's stock prices but fails on this year's data is overfit.

Test on data your model hasn't seen. If it works on new data,
it learned the pattern. If it only works on old data, it
memorized noise.

### Null result
When you don't find what you expected. This is NOT failure.
Knowing that X doesn't affect Y is valuable information — it
saves everyone else from testing the same thing.

Aegis encourages pre-committing to a negative-result plan:
"If my hypothesis is wrong, I still produce [the dataset,
the tool, the methodology paper]."


## The research process

### Pre-registration
Writing down your prediction and analysis plan BEFORE running
the experiment. This proves you didn't change your hypothesis
after seeing the results (which is surprisingly tempting).

Aegis's `pre_register()` function timestamps and hashes your
predictions so they can't be modified retroactively.

### Peer review
Having other experts check your work before it's published.
The Auditor role in Aegis simulates this — a separate AI
conversation reviews your code without knowing your reasoning.

### Reproducibility
The ability for someone else to follow your exact steps and
get the same result. Aegis's `replication_package()` bundles
everything needed. If your work isn't reproducible, it might
not be real.

### Power
The probability that your experiment will detect an effect
if one actually exists. An underpowered experiment (too few
samples) might miss a real effect and incorrectly conclude
"nothing happened."

Run `power_check()` BEFORE your experiment to make sure you
have enough data. If you don't, collecting more data is almost
always worth the effort.


## When to worry

If any of these are true, your result needs more scrutiny:
- Effect only appears in a subset of the data
- Result depends on removing specific outliers
- P-value is just barely below 0.05 (like p = 0.048)
- You ran many tests but are reporting only one
- Your sample is very different from the population you
  care about
- The effect is implausibly large
- Nobody has seen this before (extraordinary claims need
  extraordinary evidence)

None of these mean your result is wrong. They mean you should
investigate further before publishing.


## Further reading

These are free and written for non-experts:
- "Statistics Done Wrong" by Alex Reinhart (statisticsdonewrong.com)
- "Calling Bullshit" by Carl Bergstrom and Jevin West (callingbullshit.org)
- "Understanding Uncertainty" by Dennis Lindley
- Khan Academy statistics course (free, with videos)
