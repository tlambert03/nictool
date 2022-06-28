import datetime

CLEAN_TASK=


def install_task(name: str, description: str, action_id: str) -> None:
    import win32com.client

    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")
    new_task = scheduler.NewTask(0)

    # Create trigger
    start_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
    TASK_TRIGGER_TIME = 1
    trigger = new_task.Triggers.Create(TASK_TRIGGER_TIME)
    trigger.StartBoundary = start_time.isoformat()
    trigger.Repetition.Duration = 5

    # Create action
    TASK_ACTION_EXEC = 0
    action = new_task.Actions.Create(TASK_ACTION_EXEC)
    action.ID = action_id
    action.Path = 'cmd.exe'
    action.Arguments = r' "/K" %USERPROFILE%\miniforge3\Scripts\activate.bat %USERPROFILE%\miniforge3 & nic --help & exit'

    # Set parameters
    new_task.RegistrationInfo.Description = description
    new_task.RegistrationInfo.Author = "nictool"
    new_task.Settings.Enabled = True
    new_task.Settings.StopIfGoingOnBatteries = False

    # Register task
    # If task already exists, it will be updated
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_NONE = 0
    root_folder.RegisterTaskDefinition(
        name,  # Task name
        new_task,
        TASK_CREATE_OR_UPDATE,
        "",  # No user
        "",  # No password
        TASK_LOGON_NONE,
    )
