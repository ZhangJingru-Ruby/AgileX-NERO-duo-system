FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV NERO_CONTAINER=1

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash-completion \
    can-utils \
    ethtool \
    git \
    iproute2 \
    locales \
    net-tools \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    ros-humble-control-msgs \
    ros-humble-controller-manager \
    ros-humble-gripper-controllers \
    ros-humble-joint-state-publisher-gui \
    ros-humble-joint-state-broadcaster \
    ros-humble-joint-trajectory-controller \
    ros-humble-moveit \
    ros-humble-robot-state-publisher \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-topic-tools \
    ros-humble-trajectory-msgs \
    ros-humble-xacro \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    numpy \
    python-can \
    scipy

RUN mkdir -p /root/agx_arm_ws/src /workspace/nero

WORKDIR /root/agx_arm_ws

COPY docker/humble/entrypoint.sh /nero_entrypoint.sh
RUN chmod +x /nero_entrypoint.sh

ENTRYPOINT ["/nero_entrypoint.sh"]
CMD ["bash"]
