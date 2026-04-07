"""CLI for platform control."""

import click
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def cli(verbose):
    """Warehouse Environment AI Agent Platform CLI."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.option('--repo', '-r', default='.', help='Repository path')
def deploy(repo):
    """Execute full deployment pipeline."""
    from platform.platform import WarehouseEnvPlatform
    
    click.echo("Initializing platform...")
    platform = WarehouseEnvPlatform(repo)
    
    click.echo("Starting deployment...")
    result = platform.execute_full_deployment()
    
    click.echo("\n" + "=" * 60)
    if result['success']:
        click.secho("DEPLOYMENT SUCCESSFUL", fg='green', bold=True)
    else:
        click.secho("DEPLOYMENT FAILED", fg='red', bold=True)
    click.echo("=" * 60)
    
    click.echo(json.dumps(result, indent=2, default=str))
    
    return 0 if result['success'] else 1


@cli.command()
@click.option('--repo', '-r', default='.', help='Repository path')
def validate(repo):
    """Run quick validation."""
    from platform.platform import WarehouseEnvPlatform
    
    click.echo("Initializing platform...")
    platform = WarehouseEnvPlatform(repo)
    
    click.echo("Running validation...")
    result = platform.execute_quick_validation()
    
    click.echo(json.dumps(result, indent=2, default=str))
    return 0 if result['success'] else 1


@cli.command()
@click.option('--repo', '-r', default='.', help='Repository path')
def status(repo):
    """Get platform status."""
    from platform.platform import WarehouseEnvPlatform
    
    platform = WarehouseEnvPlatform(repo)
    status_info = platform.get_status()
    
    click.echo(json.dumps(status_info, indent=2, default=str))


@cli.command()
@click.option('--repo', '-r', default='.', help='Repository path')
@click.option('--output', '-o', default='deployment_report.json', help='Output file')
def report(repo, output):
    """Generate deployment report."""
    from platform.platform import WarehouseEnvPlatform
    
    platform = WarehouseEnvPlatform(repo)
    platform.save_report(output)
    click.secho(f"Report saved to {output}", fg='green')


if __name__ == '__main__':
    cli()
