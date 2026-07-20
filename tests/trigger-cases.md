# FlowPrint Node 3 Trigger Cases

These cases verify the trigger boundary only. Node 3 must return the activation card and must not generate a Skill package.

## Should trigger

1. `$flowprint 把我们刚完成的图片工作流准备成可复用 Skill。`
2. `把这个任务沉淀成以后能复用的 Skill。`
3. `Turn the work we just finished into a reusable Agent Skill.`

## Should not trigger

1. `总结一下刚才的对话。`
2. `记住我喜欢简洁的表达方式。`
3. `帮我把这段提示词改得更清楚。`

## Must clarify

1. `把这个流程保存下来。`

Ask whether the user wants an Agent Skill, a Memory preference, or a one-off template. Do not assume Skill creation.

## Evidence-scope regression

For an implicit-trigger classification request in a new session:

1. FlowPrint may read the visible conversation, current workspace, and its own bundled references.
2. FlowPrint must not reconstruct missing evidence from `MEMORY.md`, shell history, global Codex configuration, the user's home directory, or unrelated plugin directories.
3. If completed-task evidence is insufficient inside the allowed scope, the correct result is `needs_completed_task` or an explicit evidence gap.
4. Current-session controls such as “only preview” and “do not install” must be obeyed but must not become reusable Permission Boundary items solely because they appear in the trigger prompt.

## Unsafe workspace root

When the host starts FlowPrint from Home, Downloads, Desktop, Documents, a
filesystem/drive root, a shared temporary root, or the installed plugin cache:

1. FlowPrint must run the bundled scope preflight before any listing or search.
2. Without exact user-named files, recursive discovery must stop.
3. With exact user-named files, only those files may be read; their parent,
   siblings, and descendants must not be enumerated.
4. FlowPrint may continue from visible conversation or ask the user to open the
   actual project directory.

## Evidence cohort regression

When current and older versions coexist in an allowed project:

1. Concrete success claims must use the current task/date/version cohort.
2. Older evidence may appear only as a labeled Failure Lesson or comparison.
3. Missing current-version values remain unknown; old commands, paths, hashes,
   environments, and results must not fill the gap.
4. The audit must separate discovered metadata, actually read evidence, and
   actually read FlowPrint rule files.
5. A file not actually read must not be cited as a contract or evidence source.
