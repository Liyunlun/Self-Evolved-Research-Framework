
# Experiment Execution — MetaScheduler Mode

> This project uses MetaScheduler for all experiment execution and monitoring.
> The skills `experiment.run` and `experiment.monitor` are NOT available in this mode.
> Instead, experiments are submitted to and monitored by the MetaScheduler bot.

## Submitting Experiments

When experiment execution is needed (after `experiment.plan` approval or user request):

1. **Prepare submission**:
   - Ensure code is committed and pushed (`git push`)
   - Verify experiment config is in `experiments/{exp_name}/`
   - Note the conda environment name and entry command
2. **Query available resources first**:
   ```
   mb task manager <current_chat_id> "查看当前可用 GPU 资源"
   ```
3. **Based on availability, submit experiment**:
   ```
   mb task manager <current_chat_id> "项目 {project_name}，
     需要 {gpu_count}x {gpu_type}，conda {env}，
     运行 {command}，工作目录 {working_dir}"
   ```
   - GPU type/count chosen based on Step 2 results and experiment requirements
   - Do NOT hardcode defaults — let experiment needs and resource availability guide the choice
4. **MetaScheduler handles**:
   - Resource allocation (`/request-gpu`)
   - Code sync to compute node (`/sync-code`)
   - Experiment launch and monitoring (`/run-experiment`, `/monitor-experiment`)
4. **Receive results**:
   - MetaScheduler notifies on completion/failure
   - Results are available in the experiment directory on the compute node
   - Use `mb task manager <current_chat_id> "check status of task {task_id}"` for progress

## Checking Experiment Status

```
mb task manager <current_chat_id> "check status of task {task_id}"
```

Or check all active experiments:
```
mb task manager <current_chat_id> "list active experiments for {project_name}"
```

## After Experiment Completes

When MetaScheduler notifies completion:
1. Results are in `experiments/{exp_name}/results/` (synced back if remote)
2. Chain to `experiment.analyze` for result interpretation
3. Chain to `checklist.update` to mark experiment items `[x]`

## Configuration

MetaScheduler settings are in `config.yaml § metascheduler`:
```yaml
metascheduler:
  bot_name: "manager"
  default_conda_env: "research"
```
