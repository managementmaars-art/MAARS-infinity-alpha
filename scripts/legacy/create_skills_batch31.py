
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Network protocols and internals
    ('http2-internals', 'HTTP/2 internals - frames, streams, multiplexing, HPACK, server push, flow control, priority'),
    ('http3-quic', 'HTTP/3 and QUIC - UDP transport, connection migration, 0-RTT, stream multiplexing, encryption'),
    ('dns-internals', 'DNS internals - resolvers, authoritative, DNSSEC, DoH, DoT, zone transfer, TTL, split-horizon'),
    ('bgp-routing', 'BGP routing - eBGP, iBGP, path attributes, route policy, communities, EVPN, flowspec'),
    ('ospf-protocol', 'OSPF protocol - areas, LSAs, SPF, DR/BDR, authentication, OSPFv3, redistribution, tuning'),
    ('eigrp-protocol', 'EIGRP protocol - DUAL, feasible successor, metrics, neighbor tables, stub, authentication'),
    ('mpls-networking', 'MPLS networking - label switching, LDP, RSVP-TE, traffic engineering, L3VPN, L2VPN, VPLS'),
    ('ipv6-advanced', 'IPv6 advanced - addressing, NDP, SLAAC, DHCPv6, transition mechanisms, security, routing'),
    ('sdn-networking', 'SDN networking - OpenFlow, ONOS, OpenDaylight, data plane, control plane, northbound API'),
    ('network-automation', 'Network automation - NAPALM, Netmiko, Nornir, YANG, RESTCONF, NETCONF, pyATS'),
    ('netflow-ipfix', 'NetFlow/IPFIX - flow records, collectors, analyzers, sampling, export, anomaly detection'),
    ('sflow-monitoring', 'sFlow monitoring - packet sampling, counter polling, analyzers, traffic visibility'),
    ('snmp-advanced', 'SNMP advanced - MIB, OIDs, traps, v3 security, polling, bulk operations, net-snmp'),
    ('radius-diameter', 'RADIUS/Diameter - authentication, authorization, accounting, proxy, failover, 802.1X, EAP'),
    ('tacacs-protocol', 'TACACS+ protocol - authentication, authorization, accounting, cisco devices, API, failover'),
    ('ntp-ptp', 'NTP/PTP time synchronization - stratum, servers, precision, PTP hardware timestamping, grandmaster'),
    ('dhcp-advanced', 'DHCP advanced - options, relay, failover, snooping, fingerprinting, IPv6, server config'),
    ('vxlan-overlay', 'VXLAN overlay networking - VTEP, BUM traffic, EVPN control plane, multicast, anycast'),
    ('geneve-protocol', 'GENEVE protocol - overlay, TLV, variable header, NSH, hypervisor integration, offload'),
    ('segment-routing', 'Segment Routing - SRv6, MPLS SR, source routing, traffic engineering, TI-LFA, OAM'),
    ('p4-programming', 'P4 programming - data plane language, match-action, targets, parsers, behavioral model'),
    ('dpdk-advanced', 'DPDK advanced - poll mode drivers, huge pages, memory pools, packet processing, RSS'),
    ('xdp-ebpf-networking', 'XDP/eBPF networking - packet processing, load balancing, firewall, DDoS mitigation, TC'),
    ('network-telemetry', 'Network telemetry - streaming, gNMI, gNOI, OpenConfig, model-driven, analytics pipeline'),
    ('srte-traffic-eng', 'SR-TE traffic engineering - policies, candidate paths, PCEP, ODN, automated steering'),
    # Wireless and mobile protocols
    ('wifi-6-7', 'WiFi 6/6E/7 - OFDMA, MU-MIMO, BSS coloring, WPA3, 6GHz, MLO, multi-link operation'),
    ('lte-advanced-pro', 'LTE Advanced Pro - carrier aggregation, MIMO, CoMP, HetNet, MBMS, NB-IoT, CAT-M'),
    ('5g-nr-deep', '5G NR deep - NSA/SA, beamforming, massive MIMO, slicing, MEC, URLLC, mMTC, FR2'),
    ('6g-research', '6G research - terahertz, AI-native, reconfigurable surfaces, semantic comms, holographic'),
    ('bluetooth-advanced', 'Bluetooth advanced - Bluetooth 5.x, LE audio, Auracast, direction finding, mesh, isochronous'),
    ('uwb-technology', 'UWB technology - ranging, positioning, FiRa, CCC, fine ranging, secure ranging, anchor'),
    ('wi-sun-protocol', 'Wi-SUN protocol - field area network, mesh, IPv6, smart grid, IoT, ETSI, FAN'),
    ('sigfox-protocol', 'Sigfox protocol - uplink/downlink, BPSK, DBPSK, network coverage, OOB messages, API'),
    # Storage protocols
    ('nvme-protocol', 'NVMe protocol - queues, commands, namespaces, NVMe-oF, TCP, RDMA, fabric discovery'),
    ('iscsi-advanced', 'iSCSI advanced - initiators, targets, multipath, CHAP, jumbo frames, offload, boot'),
    ('fibre-channel', 'Fibre Channel - FC-SAN, zoning, NPIV, FCoE, multipathing, FSPF, fabric login'),
    ('nfs-advanced', 'NFS advanced - v4.1, v4.2, pNFS, Kerberos, ACLs, delegation, sessions, RDMA'),
    ('smb-cifs', 'SMB/CIFS - SMB 3.x, multichannel, encryption, witness, continuously available, RDMA'),
    ('ceph-storage', 'Ceph storage - RADOS, OSD, monitor, MDS, CephFS, RBD, RGW, crush map, BlueStore'),
    ('glusterfs', 'GlusterFS - bricks, volumes, translators, geo-replication, quotas, snapshots, gfapi'),
    ('lustre-fs', 'Lustre filesystem - MGS, MDS, OSS, striping, HSM, jobstat, Lnet, tuning, Lustre.yaml'),
    # Compute protocols
    ('rdma-infiniband', 'RDMA/InfiniBand - verbs, QP, CQ, MR, libibverbs, RoCE, iWARP, subnet manager'),
    ('mpi-advanced', 'MPI advanced - collectives, one-sided, persistent, partitioned, sessions, shared memory'),
    ('openmp-advanced', 'OpenMP advanced - tasks, SIMD, GPU offload, target, reduction, atomic, memory model'),
    ('opencl-advanced', 'OpenCL advanced - kernels, memory model, work groups, profiling, interop, SPIR-V'),
    ('sycl-programming', 'SYCL programming - unified shared memory, queues, kernels, buffer/accessor, reductions'),
    # Messaging protocols
    ('amqp-advanced', 'AMQP advanced - exchanges, bindings, routing keys, QoS, transactions, RabbitMQ, Qpid'),
    ('mqtt-advanced', 'MQTT advanced - v5.0, shared subscriptions, topic aliases, message expiry, flow control'),
    ('kafka-protocol', 'Kafka protocol - fetch, produce, offsets, consumer groups, rebalance, idempotency, ACL'),
    ('nats-advanced', 'NATS advanced - JetStream, KV, object store, leaf nodes, clustering, auth, connect'),
    ('zeromq-patterns', 'ZeroMQ patterns - PUB/SUB, REQ/REP, PUSH/PULL, DEALER/ROUTER, Majordomo, heartbeating'),
    ('grpc-advanced', 'gRPC advanced - bidirectional streaming, metadata, interceptors, deadlines, cancellation, health'),
    ('thrift-advanced', 'Apache Thrift - IDL, transports, protocols, servers, cross-language, versioning, TLS'),
    ('cap-n-proto', "Cap'n Proto - schema, encoding, RPC, promises, capabilities, streaming, security levels"),
    ('flatbuffers-advanced', 'FlatBuffers advanced - schema, mutations, union tables, flexbuffers, grpc plugin'),
    ('messagepack', 'MessagePack - encoding, extensions, streaming, streaming API, library comparison, schema'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
