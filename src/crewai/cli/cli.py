import click
import pkg_resources

from crewai.memory.storage.kickoff_task_outputs_storage import (
    KickoffTaskOutputsSQLiteStorage,
)

from .create_crew import create_crew
from .evaluate_crew import evaluate_crew
from .replay_from_task import replay_task_command
from .reset_memories_command import reset_memories_command
from .run_crew import run_crew
from .train_crew import train_crew


@click.group()
def crewai():
    """Top-level command group for crewai."""


@crewai.command()
@click.argument("project_name")
def create(project_name):
    """Create a new crew."""
    create_crew(project_name)


@crewai.command()
@click.option(
    "--tools", is_flag=True, help="Show the installed version of crewai tools"
)
def version(tools):
    """Show the installed version of crewai."""
    crewai_version = pkg_resources.get_distribution("crewai").version
    click.echo(f"crewai version: {crewai_version}")

    if tools:
        try:
            tools_version = pkg_resources.get_distribution("crewai-tools").version
            click.echo(f"crewai tools version: {tools_version}")
        except pkg_resources.DistributionNotFound:
            click.echo("crewai tools not installed")


@crewai.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=5,
    help="Number of iterations to train the crew",
)
@click.option(
    "-f",
    "--filename",
    type=str,
    default="trained_agents_data.pkl",
    help="Path to a custom file for training",
)
def train(n_iterations: int, filename: str):
    """Train the crew."""
    click.echo(f"Training the Crew for {n_iterations} iterations")
    train_crew(n_iterations, filename)


@crewai.command()
@click.option(
    "-t",
    "--task_id",
    type=str,
    help="Replay the crew from this task ID, including all subsequent tasks.",
)
def replay(task_id: str) -> None:
    """
    Replay the crew execution from a specific task.

    Args:
        task_id (str): The ID of the task to replay from.
    """
    try:
        click.echo(f"Replaying the crew from task {task_id}")
        replay_task_command(task_id)
    except Exception as e:
        click.echo(f"An error occurred while replaying: {e}", err=True)


@crewai.command()
def log_tasks_outputs() -> None:
    """
    Retrieve your latest crew.kickoff() task outputs.
    """
    try:
        storage = KickoffTaskOutputsSQLiteStorage()
        tasks = storage.load()

        if not tasks:
            click.echo(
                "No task outputs found. Only crew kickoff task outputs are logged."
            )
            return

        for index, task in enumerate(tasks, 1):
            click.echo(f"Task {index}: {task['task_id']}")
            click.echo(f"Description: {task['expected_output']}")
            click.echo("------")

    except Exception as e:
        click.echo(f"An error occurred while logging task outputs: {e}", err=True)


@crewai.command()
@click.option("-l", "--long", is_flag=True, help="Reset LONG TERM memory")
@click.option("-s", "--short", is_flag=True, help="Reset SHORT TERM memory")
@click.option("-e", "--entities", is_flag=True, help="Reset ENTITIES memory")
@click.option(
    "-k",
    "--kickoff-outputs",
    is_flag=True,
    help="Reset LATEST KICKOFF TASK OUTPUTS",
)
@click.option("-a", "--all", is_flag=True, help="Reset ALL memories")
def reset_memories(long, short, entities, kickoff_outputs, all):
    """
    Reset the crew memories (long, short, entity, latest_crew_kickoff_ouputs). This will delete all the data saved.
    """
    try:
        if not all and not (long or short or entities or kickoff_outputs):
            click.echo(
                "Please specify at least one memory type to reset using the appropriate flags."
            )
            return
        reset_memories_command(long, short, entities, kickoff_outputs, all)
    except Exception as e:
        click.echo(f"An error occurred while resetting memories: {e}", err=True)


@crewai.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=3,
    help="Number of iterations to Test the crew",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default="gpt-4o-mini",
    help="LLM Model to run the tests on the Crew. For now only accepting only OpenAI models.",
)
def test(n_iterations: int, model: str):
    """Test the crew and evaluate the results."""
    click.echo(f"Testing the crew for {n_iterations} iterations with model {model}")
    evaluate_crew(n_iterations, model)


@crewai.command()
def run():
    """Run the crew."""
    click.echo("Running the crew")
    run_crew()


if __name__ == "__main__":
    crewai()
