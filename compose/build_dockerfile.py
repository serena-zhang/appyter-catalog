import os
from textwrap import dedent

def build_dockerfile(template_path, config):
  dockerfile_parts = ['''
    FROM ubuntu
  ''', '''
    ENV DEBIAN_FRONTEND "noninteractive"
    ENV TZ "America/New_York"
  ''', '''
    RUN set -x \\
        && echo "Preparing system..." \\
        && apt-get -y update \\
        && apt-get -y install git python3-pip python3-dev \\
        && rm -rf /var/lib/apt/lists/* \\
        && pip3 install --upgrade pip
  ''', '''
    RUN set -x \\
      && echo "Installing jupyter kernel..." \\
      && pip3 install ipykernel \\
      && python3 -m ipykernel install
  ''']
  if os.path.isfile(os.path.join(template_path, 'deps.txt')):
    dockerfile_parts.append('''
      ADD deps.txt /app/deps.txt
      RUN set -x \\
        && echo "Installing system dependencies from deps.txt..." \\
        && apt-get -y update \\
        && apt-get -y install $(grep -v '^#' /app/deps.txt) \\
        && rm -rf /var/lib/apt/lists/* \\
        && rm /app/deps.txt
    ''')
  if os.path.isfile(os.path.join(template_path, 'setup.R')):
    dockerfile_parts.append('''
      ADD setup.R /app/setup.R
      RUN set -x \\
        && echo "Installing R..." \\
        && apt-get -y update \\
        && apt-get -y install r-base \\
        && rm -rf /var/lib/apt/lists/* \\
        && echo "Setting up R with setup.R..." \\
        && R -e "source('/app/setup.R')" \\
        && rm /app/setup.R
    ''')
  if os.path.isfile(os.path.join(template_path, 'requirements.txt')):
    dockerfile_parts.append('''
      ADD requirements.txt /app/requirements.txt
      RUN set -x \\
        && echo "Installing python dependencies from requirements.txt..." \\
        && pip3 install -Ivr /app/requirements.txt \\
        && rm /app/requirements.txt
    ''')
  dockerfile_parts.append('''
    ARG jupyter_template_version=git+git://github.com/Maayanlab/jupyter-template.git
    RUN set -x \\
      && echo "Installing jupyter-template..." \\
      && pip3 install -Iv ${jupyter_template_version}
  ''')
  dockerfile_parts.append('''
    WORKDIR /app
    EXPOSE 80
  ''')
  dockerfile_parts.append('''
    ENV PREFIX "/"
    ENV HOST "0.0.0.0"
    ENV PORT "80"
    ENV DEBUG "false"
  ''')
  dockerfile_parts.append('''
    COPY . /app
  ''')
  dockerfile_parts.append(f'''
    CMD [ "jupyter-template", "--profile={config['template'].get('profile', 'default')}", "{config['template']['file']}" ]
  ''')
  return '\n\n'.join(map(str.strip, map(dedent, dockerfile_parts)))

if __name__ == '__main__':
  import sys
  import json
  template = sys.argv[1]
  template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', template)
  config = json.load(open(os.path.join(template_path, 'template.json'), 'r'))
  print(build_dockerfile(template_path, config))