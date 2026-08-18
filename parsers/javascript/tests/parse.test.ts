import { parse } from '../src/parse';

describe('ZEON Parser', () => {
    test('parses basic key-value pairs', () => {
        const input = `
name="Zeon"
version=1
is_active=true
`;
        const result = parse(input);
        expect(result).toEqual({
            name: "Zeon",
            version: 1,
            is_active: true
        });
    });

    test('parses tabular block', () => {
        const input = `
users[]
  id name
  1 "alice"
  2 "bob"
`;
        const result = parse(input);
        expect(result).toEqual({
            users: [
                { id: 1, name: "alice" },
                { id: 2, name: "bob" }
            ]
        });
    });

    test('parses inline dictionaries', () => {
        const input = `
config(timeout=30 retry=true)
`;
        const result = parse(input);
        expect(result).toEqual({
            config: {
                timeout: 30,
                retry: true
            }
        });
    });

    test('parses inline arrays', () => {
        const input = `
tags=[ "api" "v1" ]
`;
        const result = parse(input);
        expect(result).toEqual({
            tags: ["api", "v1"]
        });
    });

    test('parses extreme cases perfectly', () => {
        const input = `project_name="ZEON Edge Cases"
version=1.0
is_active=True
deleted_at=None
config
  timeout retries
  30 5
users[]
  id name preferences(theme notifications)
  1 Maria (light True)
  2 Jose (dark False)
coordinates[][]
  10.0 20.0
  30.0 40.0 
mixed_data=[1 hello (flag=True) [2 3]]
tensor=[[[1 2] [3 4]]]`;
        const result = parse(input);
        expect(result).toEqual({
            project_name: "ZEON Edge Cases",
            version: 1.0,
            is_active: true,
            deleted_at: null,
            config: {
                timeout: 30,
                retries: 5
            },
            users: [
                {
                    id: 1,
                    name: "Maria",
                    preferences: { theme: "light", notifications: true }
                },
                {
                    id: 2,
                    name: "Jose",
                    preferences: { theme: "dark", notifications: false }
                }
            ],
            coordinates: [
                [10.0, 20.0],
                [30.0, 40.0]
            ],
            mixed_data: [
                1, "hello", { flag: true }, [2, 3]
            ],
            tensor: [[[1, 2], [3, 4]]]
        });
    });
});
