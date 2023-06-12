# funnelbeam
## Set up project
# Build docker image
- docker build -t funnelbeam  .
# Run script
- docker run -e COMPANY=Netflix funnelbeam
# Run test
- docker run funnelbeam pytest tests/
## I get all valid links, after that I try to get all apps from each link and combine data if they are already appeared in another category link
## Still need more tests and improce logging
