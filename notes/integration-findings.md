# DeepAgents integration findings

Goal:
Find the smallest believable Aegis integration point.

What to verify:
- main entrypoint
- where model calls are orchestrated
- where middleware is inserted
- where state/messages flow
- best place for baseline vs Aegis comparison

Initial hypothesis:
Use create_deep_agent(..., middleware=[...]) as the runtime insertion point.

What we want to avoid:
- forking DeepAgents internals
- rewriting graph assembly
- replacing model/provider behavior
