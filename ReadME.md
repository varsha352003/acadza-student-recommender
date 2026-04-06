# Acadza Student Recommender System

## Overview
This project is a FastAPI-based adaptive learning recommendation system designed for Acadza’s JEE/NEET preparation workflow. The system analyzes a student’s performance across multiple tests and assignments, identifies chapter-level weaknesses, and recommends the next best study actions in the form of DOSTs (Dynamic Optimized Study Tasks). The goal of the build was not just to recommend questions, but to create a **step-by-step personalized learning path** that reflects the student’s academic weaknesses, test-taking behavior, and recent performance trends.

The solution is built with a modular backend structure so that the recommendation logic, analysis logic, question selection, and API routes remain independently testable and easy to extend.

---

## My Approach to the Build Task
I approached the build in three layers.

The first layer was **data normalization and cleanup**. Since the input files intentionally contain inconsistent formats, I first created reusable utility functions to normalize marks and question IDs. This ensured that downstream analytics logic always worked on clean numerical values.

The second layer was **student performance analysis**. For each student, I aggregated all historical attempts and derived chapter-wise and session-wise signals such as average score, completion rate, skipped percentage, and average time per question. Instead of using only a direct threshold-based rule system, I created a **chapter priority vector**, where each chapter receives a weakness priority score.

This score combines multiple learning-risk signals:
- low academic score
- slow solving speed
- frequent skipping
- incomplete sessions
- recent decline in trend

The purpose of this vector is to rank chapters by **learning urgency**, so the system can decide which chapter should be targeted first.

The third layer was **DOST sequencing**. Once the top-priority chapter is identified, the system generates a step-by-step study flow. For example, if the student is weak conceptually, the sequence starts with `formula`, then `concept`, followed by `practiceAssignment`. If the issue is speed, the sequence introduces `clickingPower` and `speedRace`. This makes the recommendations product-oriented rather than just question-matching.

---

## How I Decided Which DOSTs to Recommend and in What Order
The DOST order is driven by the dominant weakness pattern of the top-priority chapter.

If the student has low marks in the chapter, the system assumes the issue starts from concept recall, so it first recommends **formula revision**, then **concept reinforcement**, and only then moves into **targeted assignments**.

If the student is solving correctly but too slowly, the system prioritizes **speed-building DOSTs** such as `clickingPower` and `speedRace`.

If the student’s recent attempts show a declining trend, I insert a `revision` DOST before practice to reinforce retention.

For incomplete sessions, I add a shorter `practiceTest` near the end so the student rebuilds stamina and completion consistency.

This sequencing logic was chosen to simulate how a real adaptive EdTech product would gradually move a learner from recall → understanding → application → speed.

---

## How I Handled the Messy Marks Field and Assumptions Made
The `marks` field had multiple inconsistent formats such as `68/100`, `+52 -12`, `34/75 (45.3%)`, raw integers, and numeric strings.

To standardize this, I built a `normalize_marks()` helper.

The assumptions used were:
- if percentage already exists in brackets, use it directly
- if marks are in `x/y`, convert to percentage
- if marks are in positive-negative format, compute net score
- numeric values are assumed already on a 0–100 scale
- all final values are clamped between 0 and 100

These assumptions were intentionally heuristic because the dataset did not provide a universal scoring denominator for every format. The goal was to keep the normalization deterministic, explainable, and robust for downstream ranking.

---

## My Debug Process
The debug task involved a recommender that used cosine similarity between student weakness vectors and question vectors.

The code executed successfully, so the issue was not syntactic but logical. My first debugging step was to compare recommendation overlap across students with very different weakness profiles. The overlap was unexpectedly high, which suggested that personalization was being lost somewhere in the profile construction stage.

I traced the issue to the normalization step inside the recommendation function. The student-specific adjusted profile was correctly computed as:

`student_vector - cohort_average`

However, during normalization, this personalized vector was accidentally overwritten by the **cohort baseline vector itself**. As a result, all students were effectively being compared using the same normalized cohort vector.

The fix was to normalize the already computed `student_profile` instead of the cohort average.

After the fix, recommendation overlap dropped to zero across students with different weakness profiles, which confirmed that personalization was restored.

One thing I initially checked but ruled out was cosine similarity itself, since the ranking behavior was mathematically valid. The actual issue was the variable overwrite during normalization.

I did take some help from AI during the development process, mainly to speed up the initial project structuring and to explore a few possible recommendation approaches. It helped me think through how to separate the analyzer, recommender, and question-selection logic cleanly, and also gave me a few ideas on how the DOST flow could be sequenced in a more adaptive way.

For the debugging part, I did not rely on AI alone. I first looked at the recommendation overlap manually because the outputs felt too similar for students with very different weakness profiles. I then used AI to cross-check a few possible causes, but some of those early suggestions were not actually the root problem. The real issue became clear only after I traced the vector normalization logic line by line myself and compared the outputs before and after the fix.

So overall, AI helped me move faster during exploration, but I made sure to manually verify the logic, especially for the bug fix and the final recommendation flow.

---

## What I Would Improve Given More Time
Given more time, I would improve the system in four major ways.

First, I would make the priority score weights configurable through `dost_config.json` so that product teams can tune recommendation behavior without code changes.

Second, I would incorporate **question-level historical outcomes**, such as whether a recommended question actually improved the student’s next-session score.

Third, I would upgrade the heuristic chapter priority vector into a **learned ranking model** using historical engagement and improvement data.

Finally, I would add automated tests for normalization edge cases, recommendation sequencing, and question deduplication so the system becomes production-ready.

---

## Running the Project
Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI app:

```bash
uvicorn app.main:app --reload
```

Swagger docs will be available at:

```text
http://127.0.0.1:8000/docs
```

