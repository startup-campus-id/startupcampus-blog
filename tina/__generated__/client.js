import { createClient } from "tinacms/dist/client";
import { queries } from "./types";
export const client = createClient({ url: "http://localhost:4001/graphql", token: "321d65728697e1d630f0c33fd68913846f111e68", queries });
export default client;
