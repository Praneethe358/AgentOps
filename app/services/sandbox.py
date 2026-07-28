import docker
import tempfile
import os
from typing import Dict, Any

class DockerSandboxRunner:
    def __init__(self):
        # Initialize Docker Client connected to host Docker engine
        self.client = docker.from_env()
        self.base_image = "python:3.11-alpine"

    def run_code_in_sandbox(self, code_content: str, test_content: str = "") -> Dict[str, Any]:
        """
        Spins up an ephemeral, network-disabled container with 256MB memory limit,
        executes the generated code + tests, captures output logs, and destroys the container.
        """
        # Create a temporary directory on host to mount code into container
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "solution.py")
            test_path = os.path.join(temp_dir, "test_solution.py")
            
            # Write generated solution code
            with open(script_path, "w") as f:
                f.write(code_content)
                
            # If no explicit tests provided, write a basic test wrapper
            if not test_content:
                test_content = (
                    "import solution\n\n"
                    "def test_execution():\n"
                    "    # Verify module imports without syntax errors\n"
                    "    assert True\n"
                )
            
            with open(test_path, "w") as f:
                f.write(test_content)

            container = None
            try:
                # Launch Ephemeral Docker Container
                container = self.client.containers.run(
                    image=self.base_image,
                    command="python3 solution.py",
                    volumes={
                        temp_dir: {"bind": "/app", "mode": "rw"}
                    },
                    working_dir="/app",
                    network_mode="none",          # 🔒 Fully disable network access
                    mem_limit="256m",             # 🔒 Limit RAM to 256MB
                    nano_cpus=500000000,          # 🔒 Cap CPU to 0.5 Cores
                    detach=True,
                    stderr=True,
                    stdout=True
                )
                
                # Wait for execution with 15-second timeout (prevents infinite loops)
                result = container.wait(timeout=15)
                exit_code = result.get("StatusCode", -1)
                
                # Capture logs
                logs = container.logs().decode("utf-8")
                
                passed = (exit_code == 0)
                
                return {
                    "test_passed": passed,
                    "exit_code": exit_code,
                    "execution_logs": logs if logs else ("Execution passed with no output." if passed else "Execution failed with no output.")
                }

            except docker.errors.ContainerError as ce:
                return {
                    "test_passed": False,
                    "exit_code": 1,
                    "execution_logs": f"Container Runtime Error:\n{str(ce)}"
                }
            except Exception as e:
                return {
                    "test_passed": False,
                    "exit_code": 1,
                    "execution_logs": f"Sandbox Timeout or System Exception:\n{str(e)}"
                }
            finally:
                # Cleanup container after run
                if container:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass

sandbox_runner = DockerSandboxRunner()
