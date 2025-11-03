``` mermaid
    flowchart LR
    User -- tcp/443 --> LB --> WebServer
```

``` mermaid
    flowchart LR
        subgraph PublicInternet
            User
        end
        subgraph LoadBalancerZone
            LB
        end
        subgraph WebServerZone
            WebServer
        end
        User --> LB --> WebServer
```

``` mermaid
    flowchart LR
        subgraph PublicInternet
            User
        end
        subgraph LoadBalancerZone
            LB
        end
        subgraph WebServerZone
            WebServerA
            WebServerB
        end
        User --> LB
        LB --> WebServerA
        LB --> WebServerB
```
